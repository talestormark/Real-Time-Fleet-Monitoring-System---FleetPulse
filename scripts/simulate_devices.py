#!/usr/bin/env python3
"""
Telemetry Simulator for FleetPulse
Generates realistic device telemetry data for testing and demos.
"""

import asyncio
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Tuple
import httpx
import math


class DeviceSimulator:
    """Simulates a single device generating telemetry."""

    def __init__(self, device_id: str, city: str, start_pos: Tuple[float, float]):
        self.device_id = device_id
        self.city = city
        self.lat, self.lon = start_pos
        self.battery_pct = random.randint(60, 100)
        self.temp_c = random.uniform(18, 28)
        self.speed_mps = 0.0
        self.is_moving = False
        self.target_pos = None

    def update_position(self, time_delta: float):
        """Update device position based on movement."""
        if not self.is_moving:
            # Randomly start moving
            if random.random() < 0.1:  # 10% chance to start moving
                self.is_moving = True
                # Random destination within ~500m
                self.target_pos = (
                    self.lat + random.uniform(-0.005, 0.005),
                    self.lon + random.uniform(-0.005, 0.005)
                )
                self.speed_mps = random.uniform(2.0, 8.0)  # 2-8 m/s
            return

        # Move towards target
        if self.target_pos:
            lat_diff = self.target_pos[0] - self.lat
            lon_diff = self.target_pos[1] - self.lon
            distance = math.sqrt(lat_diff**2 + lon_diff**2)

            if distance < 0.0001:  # Reached target
                self.is_moving = False
                self.speed_mps = 0.0
                self.target_pos = None
            else:
                # Move towards target
                move_distance = self.speed_mps * time_delta / 111000  # approx meters to degrees
                ratio = min(move_distance / distance, 1.0)
                self.lat += lat_diff * ratio
                self.lon += lon_diff * ratio

                # Vary speed slightly
                self.speed_mps += random.uniform(-0.5, 0.5)
                self.speed_mps = max(0, min(self.speed_mps, 10.0))

    def update_battery(self, time_delta: float):
        """Update battery level based on usage."""
        if self.is_moving:
            # Battery drains faster when moving
            drain_rate = 0.01 * (self.speed_mps / 5.0)  # ~0.6-1.2% per minute at full speed
            self.battery_pct -= drain_rate * (time_delta / 60)
        else:
            # Slow drain when idle
            self.battery_pct -= 0.001 * (time_delta / 60)

        # Occasionally "charge" the device
        if not self.is_moving and random.random() < 0.01:  # 1% chance
            self.battery_pct = min(100, self.battery_pct + random.uniform(5, 15))

        self.battery_pct = max(0, min(100, self.battery_pct))

    def generate_reading(self) -> dict:
        """Generate a telemetry reading."""
        # Simulate occasional impacts
        accel_g = random.uniform(0.8, 1.2)
        if self.is_moving and random.random() < 0.001:  # 0.1% chance of impact
            accel_g = random.uniform(3.5, 6.0)

        # Temperature varies slightly
        self.temp_c += random.uniform(-0.5, 0.5)
        self.temp_c = max(15, min(35, self.temp_c))

        return {
            "device_id": self.device_id,
            "ts": datetime.utcnow().isoformat() + "Z",
            "lat": round(self.lat, 6),
            "lon": round(self.lon, 6),
            "battery_pct": int(self.battery_pct),
            "speed_mps": round(self.speed_mps, 2),
            "temp_c": round(self.temp_c, 1),
            "accel_g": round(accel_g, 2)
        }

    def step(self, time_delta: float):
        """Advance simulation by time_delta seconds."""
        self.update_position(time_delta)
        self.update_battery(time_delta)


class FleetSimulator:
    """Manages simulation of multiple devices."""

    CITY_CENTERS = {
        "New York": (40.7128, -74.0060),
        "San Francisco": (37.7749, -122.4194),
        "Chicago": (41.8781, -87.6298),
        "Austin": (30.2672, -97.7431),
        "Seattle": (47.6062, -122.3321),
    }

    def __init__(self, num_devices: int, api_url: str, speed_multiplier: float = 1.0):
        self.num_devices = num_devices
        self.api_url = api_url
        self.speed_multiplier = speed_multiplier
        self.devices: List[DeviceSimulator] = []
        self.initialize_devices()

    def initialize_devices(self):
        """Create simulated devices."""
        cities = list(self.CITY_CENTERS.keys())

        for i in range(self.num_devices):
            city = random.choice(cities)
            center_lat, center_lon = self.CITY_CENTERS[city]

            # Scatter devices within ~2km of city center
            start_pos = (
                center_lat + random.uniform(-0.01, 0.01),
                center_lon + random.uniform(-0.01, 0.01)
            )

            device_type = "bike" if i % 2 == 0 else "scooter"
            device_id = f"{device_type}-sim-{i+1:03d}"

            device = DeviceSimulator(device_id, city, start_pos)
            self.devices.append(device)

    async def register_devices(self):
        """Register all devices with the API."""
        print(f"Registering {len(self.devices)} devices...")

        async with httpx.AsyncClient() as client:
            for device in self.devices:
                device_data = {
                    "id": device.device_id,
                    "name": f"{device.city} {device.device_id.split('-')[0].title()} {device.device_id.split('-')[2]}",
                    "model": "Urban Cruiser v2" if "bike" in device.device_id else "ZipZap X1",
                    "firmware_version": "2.1.0",
                    "city": device.city
                }

                try:
                    response = await client.post(
                        f"{self.api_url}/devices",
                        json=device_data,
                        timeout=5.0
                    )
                    if response.status_code == 201:
                        print(f"✓ Registered {device.device_id}")
                    elif response.status_code == 400:
                        print(f"- {device.device_id} already exists")
                    else:
                        print(f"✗ Failed to register {device.device_id}: {response.status_code}")
                except Exception as e:
                    print(f"✗ Error registering {device.device_id}: {e}")

    async def send_telemetry(self, reading: dict):
        """Send a telemetry reading to the API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/ingest",
                    json=reading,
                    timeout=5.0
                )
                return response.status_code == 200
            except Exception as e:
                print(f"Error sending telemetry: {e}")
                return False

    async def run(self, duration_seconds: int = None):
        """Run the simulation."""
        print(f"\nStarting simulation with {len(self.devices)} devices...")
        print(f"Speed multiplier: {self.speed_multiplier}x")
        print(f"Sending telemetry to: {self.api_url}/ingest\n")

        update_interval = 5.0  # Send telemetry every 5 seconds
        elapsed = 0
        readings_sent = 0
        start_time = datetime.now()

        try:
            while True:
                if duration_seconds and elapsed >= duration_seconds:
                    break

                # Step all devices forward
                time_delta = update_interval * self.speed_multiplier
                for device in self.devices:
                    device.step(time_delta)

                # Send telemetry for all devices
                tasks = []
                for device in self.devices:
                    reading = device.generate_reading()
                    tasks.append(self.send_telemetry(reading))

                results = await asyncio.gather(*tasks)
                successful = sum(results)
                readings_sent += successful

                elapsed += update_interval

                # Print status
                avg_battery = sum(d.battery_pct for d in self.devices) / len(self.devices)
                moving_count = sum(1 for d in self.devices if d.is_moving)
                runtime = (datetime.now() - start_time).total_seconds()

                print(f"[{int(elapsed)}s] Sent {successful}/{len(self.devices)} readings | "
                      f"Moving: {moving_count} | Avg Battery: {avg_battery:.1f}% | "
                      f"Total sent: {readings_sent} | Rate: {readings_sent/runtime:.1f}/s")

                # Wait before next update
                await asyncio.sleep(update_interval)

        except KeyboardInterrupt:
            print("\n\nSimulation stopped by user.")
            print(f"Total readings sent: {readings_sent}")
            print(f"Runtime: {(datetime.now() - start_time).total_seconds():.1f}s")


def main():
    parser = argparse.ArgumentParser(description="FleetPulse Telemetry Simulator")
    parser.add_argument("--devices", type=int, default=10, help="Number of devices to simulate")
    parser.add_argument("--api-url", default="http://localhost:8000/api/v1", help="API base URL")
    parser.add_argument("--speed", type=float, default=1.0, help="Simulation speed multiplier")
    parser.add_argument("--duration", type=int, help="Run for specified seconds (default: infinite)")
    parser.add_argument("--register-only", action="store_true", help="Only register devices, don't send telemetry")

    args = parser.parse_args()

    simulator = FleetSimulator(args.devices, args.api_url, args.speed)

    # Run async simulation
    async def run_simulation():
        await simulator.register_devices()
        if not args.register_only:
            await simulator.run(args.duration)

    asyncio.run(run_simulation())


if __name__ == "__main__":
    main()
