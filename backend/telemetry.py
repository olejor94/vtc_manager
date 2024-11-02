import websockets
import asyncio
import json

class ETS2Telemetry:
    def __init__(self, vtc_manager):
        self.vtc = vtc_manager
        self.current_job = None
        
    async def connect_to_game(self):
        uri = "ws://localhost:20808/api/ets2/telemetry"
        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    data = await websocket.recv()
                    await self.process_telemetry(json.loads(data))
                except websockets.ConnectionClosed:
                    print("Connection to ETS2 lost. Reconnecting...")
                    await asyncio.sleep(5)
                    
    async def process_telemetry(self, data):
        if not self.current_job and data['game']['connected']:
            if data['job']['income'] > 0:
                self.current_job = {
                    'user_id': self.vtc.current_user[0],
                    'source': data['job']['sourceCity'],
                    'destination': data['job']['destinationCity'],
                    'cargo': data['job']['cargo'],
                    'income': data['job']['income'],
                    'distance': data['job']['distance'],
                    'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'in_progress'
                }
                
        if self.current_job and data['job']['delivered']:
            self.current_job['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.current_job['fuel_used'] = data['truck']['fuelUsed']
            self.current_job['status'] = 'completed'
            self.save_job()
            self.current_job = None

    def save_job(self):
        self.vtc.cursor.execute('''
            INSERT INTO jobs (user_id, source, destination, cargo, income, distance, 
                            fuel_used, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.current_job['user_id'], self.current_job['source'],
            self.current_job['destination'], self.current_job['cargo'],
            self.current_job['income'], self.current_job['distance'],
            self.current_job['fuel_used'], self.current_job['start_time'],
            self.current_job['end_time'], self.current_job['status']
        ))
        self.vtc.conn.commit()
