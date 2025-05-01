from channels.layers import get_channel_layer
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "convoy_game.settings")

import django
django.setup()

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async 
from .conway import ConwayGame 
from .models import SavedGameState 
from django.contrib.auth.models import User 

shared_game = ConwayGame(width = 50, height = 50)

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # Only allow authenticated users to connect fully
        if not self.user or not self.user.is_authenticated:
             print("WebSocket connection rejected: User not authenticated.")
             await self.close()
             return

        print(f"WebSocket connection accepted for user: {self.user.username}")
        self.simulation_task = None
        self.simulation_speed = 0.5 

        await self.channel_layer.group_add("game_group", self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
             'type': 'connection_established',
             'message': 'Connected to game server.'
        }))


    async def disconnect(self, close_code):
        print(f"WebSocket disconnected for user: {self.user.username if self.user else 'anonymous'}")
        # Clean up the simulation task if it's running
        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                 await self.simulation_task # Wait for task to finish cancelling
            except asyncio.CancelledError:
                 print("Simulation task cancelled on disconnect.")
            self.simulation_task = None
            await self.channel_layer.group_discard("game_group", self.channel_name)



    async def receive(self, text_data):
        if not self.user or not self.user.is_authenticated:
             await self.close()
             return

        try:
            data = json.loads(text_data)
            action = data.get('action')
            print(f"Received action '{action}' from user {self.user.username}")

            # Game Actions
            if action == 'toggle_cell':
                if 'row' in data and 'col' in data and 'state' in data:
                    row, col, state = int(data['row']), int(data['col']), bool(data['state'])
                    shared_game.set_cell(row, col, state)
                    await self.send_grid_update()
                else:
                    await self.send_error("Missing data for toggle_cell action.")

            elif action == 'get_initial_state': 
                 await self.send_initial_state() 

            #  Admin/Simulation Control Actions 
            # Check if user is admin (using username 'Admin')
            is_admin = self.user.username == "Admin"

            if action == 'start_simulation' and is_admin:
                await self.start_simulation()
            elif action == 'stop_simulation' and is_admin:
                await self.stop_simulation()
            elif action == 'clear_grid' and is_admin:
                await self.clear_grid()

            # --- Save/Load Actions (Authenticated Users) ---
            elif action == 'get_saved_states':
                 await self.send_saved_states_list()
            elif action == 'save_state':
                 name = data.get('name')
                 if name:
                      await self.save_game_state(name)
                 else:
                      await self.send_error("Save name not provided.")
            elif action == 'load_state':
                 save_id = data.get('save_id') 
                 if save_id:
                      try:
                          save_id_int = int(save_id)
                          await self.load_game_state(save_id_int)
                      except ValueError:
                          await self.send_error("Invalid Save ID format.")
                 else:
                      await self.send_error("Save ID/name not provided.")

            #Unknown Action
            elif not is_admin and action in ['start_simulation', 'stop_simulation', 'clear_grid']:
                 await self.send_error("Permission denied for simulation control.")
            else:
                print(f"Unknown or unhandled action received: {action}")

        except json.JSONDecodeError:
            print("Failed to decode JSON message.")
            await self.send_error("Invalid JSON format.")
        except Exception as e:
            import traceback
            print(f"Error processing message for user {self.user.username}: {e}")
            traceback.print_exc()
            await self.send_error(f"An internal error occurred.") 


    async def send_grid_update(self):
        """Sends the current grid state to the client."""
        if self.channel_layer:
             try:
                  grid_data = shared_game.get_grid_for_json() 
                  await self.channel_layer.group_send(
                     "game_group",
                     {
                         "type": "broadcast_grid_update",
                         "grid": grid_data
                     }
                 )
             except Exception as e:
                  print(f"Error broadcasting grid update: {e}")


    async def send_initial_state(self):
         """Sends the initial grid state when requested."""
         if self.channel_layer and self.channel_name:
              try:
                   grid_data = shared_game.get_grid_for_json()
                   await self.send(text_data=json.dumps({
                       'type': 'initial_state',
                       'grid': grid_data
                   }))
              except Exception as e:
                  print(f"Error sending initial state: {e}")


    async def simulation_loop(self):
        """Continuously updates and sends the grid state."""
        print(f"Simulation loop starting for {self.user.username} with speed {self.simulation_speed}s")
        while True:
            try:
                shared_game.update_grid()
                await self.send_grid_update()
                await asyncio.sleep(self.simulation_speed) 
            except asyncio.CancelledError:
                print(f"Simulation loop cancelled for {self.user.username}")
                raise 
            except Exception as e:
                print(f"Error in simulation loop for {self.user.username}: {e}")
                await self.send_error("An error occurred during simulation.")
                break 


    async def start_simulation(self):
        if not self.simulation_task or self.simulation_task.done():
            print(f"Starting simulation for {self.user.username}")
            # Create and store the task
            self.simulation_task = asyncio.create_task(self.simulation_loop())
            # Optionally, send feedback to the client
            await self.send(text_data=json.dumps({'type': 'simulation_started'}))
        else:
            print(f"Simulation already running for {self.user.username}")
            await self.send_error("Simulation is already running.")


    async def stop_simulation(self):
        if self.simulation_task and not self.simulation_task.done():
            print(f"Stopping simulation for {self.user.username}")
            self.simulation_task.cancel()
            try:
                 # Wait for the task to acknowledge cancellation
                 await asyncio.wait_for(self.simulation_task, timeout=1.0)
            except asyncio.CancelledError:
                 print("Simulation task successfully cancelled.")
            except asyncio.TimeoutError:
                 print("Warning: Simulation task did not cancel within timeout.")
            except Exception as e:
                 print(f"Exception while waiting for simulation task cancellation: {e}")
            finally:
                 self.simulation_task = None
            # Optionally, send feedback to the client
            await self.send(text_data=json.dumps({'type': 'simulation_stopped'}))
        else:
            print(f"Simulation not running or already stopped for {self.user.username}")
            await self.send_error("Simulation is not running.")


    async def clear_grid(self):
         print(f"Clearing grid for {self.user.username}")
         await self.stop_simulation() # Stop simulation before clearing
         shared_game.clear_grid()
         await self.send_grid_update() # Send the cleared grid state
         # Optionally, send feedback
         await self.send(text_data=json.dumps({'type': 'grid_cleared'}))


    async def send_error(self, message):
         """Sends an error message to the client."""
         if self.channel_layer and self.channel_name:
             try:
                 await self.send(text_data=json.dumps({
                     'type': 'error',
                     'message': message
                 }))
             except Exception as e:
                 print(f"Error sending error message: {e}")


    # --- Database Interaction Methods (using @database_sync_to_async) ---
    @database_sync_to_async
    def _get_saved_states_from_db(self):
         """Fetches saved states for the current user from the database."""
         # Ensure self.user is valid before querying
         if not self.user or not self.user.is_authenticated:
             return []
         # Return list of dicts with id and name for the frontend
         return list(SavedGameState.objects.filter(user=self.user).values('id', 'name').order_by('-timestamp'))

    @database_sync_to_async
    def _save_state_to_db(self, name, grid_data):
         """Saves the current grid state to the database."""
         if not self.user or not self.user.is_authenticated:
              return False, "User not authenticated."
         try:
             # Serialize the grid data to JSON string
             grid_json = json.dumps(grid_data)
             # Use update_or_create to handle saving over an existing name
             save_state, created = SavedGameState.objects.update_or_create(
                 user=self.user,
                 name=name,
                 defaults={'grid_state_json': grid_json}
             )
             print(f"Game state '{name}' {'created' if created else 'updated'} for user {self.user.username}")
             return True, f"State '{name}' saved successfully."
         except Exception as e:
             print(f"Database error saving state for {self.user.username}: {e}")
             return False, f"Failed to save state: {e}"

    @database_sync_to_async
    def _load_state_from_db(self, save_id):
         """Loads a specific grid state from the database."""
         if not self.user or not self.user.is_authenticated:
              return None 
         try:
             saved_state = SavedGameState.objects.get(id=int(save_id), user=self.user)
             grid_data = json.loads(saved_state.grid_state_json)
             print(f"Loaded state '{saved_state.name}' for user {self.user.username}")
             return grid_data
         except SavedGameState.DoesNotExist:
             print(f"Save state with ID {save_id} not found for user {self.user.username}")
             return None # Indicate not found
         except json.JSONDecodeError:
             print(f"Error decoding JSON for saved state ID {save_id} for user {self.user.username}")
             return None # Indicate corrupt data
         except ValueError:
             print(f"Invalid save_id format: {save_id}")
             return None # Indicate invalid ID format
         except Exception as e:
             print(f"Database error loading state for {self.user.username}: {e}")
             return None # Indicate other DB error


    async def send_saved_states_list(self):
         """Sends the list of saved game states to the client."""
         saved_states = await self._get_saved_states_from_db()
         await self.send(text_data=json.dumps({
             'type': 'saved_states_list',
             'states': saved_states
         }))

    async def save_game_state(self, name):
         """Handles the 'save_state' action."""
         grid_data = shared_game.get_grid_for_json() # Get current state
         success, message = await self._save_state_to_db(name, grid_data)
         feedback_type = 'save_success' if success else 'error'
         await self.send(text_data=json.dumps({
             'type': feedback_type,
             'message': message
         }))
         if success:
             await self.send_saved_states_list()


    async def load_game_state(self, save_id):
         """Handles the 'load_state' action."""
         print(f"Attempting to load state ID {save_id} for user {self.user.username}")
         await self.stop_simulation() # Stop simulation before loading
         loaded_grid_data = await self._load_state_from_db(save_id)

         if loaded_grid_data is not None:
             shared_game.set_grid_from_data(loaded_grid_data) 
             print(f"Successfully loaded grid state ID {save_id} into game instance for {self.user.username}")
             await self.send_grid_update() # Send the loaded state to the client
             await self.send(text_data=json.dumps({
                 'type': 'load_success',
                 'message': 'State loaded successfully.'
             }))
         else:
             await self.send_error(f"Could not load saved state with ID {save_id}.")

    async def broadcast_grid_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'grid_update',
            'grid': event['grid']
        }))

