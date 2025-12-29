#!/usr/bin/env python3
"""
Simplified Telemetry Simulator for existing FleetPulse devices.
Uses the devices already seeded in the database.
"""

import asyncio
import random
import argparse
from datetime import datetime
from typing import List, Tuple
import httpx
import math


class DeviceSimulator:
    """Simulates a single device generating telemetry."""

    CITY_CENTERS = {
        "New York": (40.7128, -74.0060),
        "San Francisco": (37.7749, -122.4194),
    }

    def __init__(self, device_id: str, city: str):
        self.device_id = device_id
        self.city = city
        center_lat, center_lon = self.CITY_CENTERS.get(city, (40.7128, -74.0060))

        # Random start position near city center
        self.lat = center_lat + random.uniform(-0.01, 0.01)
        self.lon = center_lon + random.uniform(-0.01, 0.01)
        self.battery_pct = random.randint(60, 100)
        self.temp_c = random.uniform(18, 28)
        self.speed_mps = 0.0
        self.is_moving = False
        self.target_pos = None

    def update_position(self, time_delta: float):
        """Update device position based on movement."""
        if not self.is_moving:
            # Randomly start moving
            if random.random() < 0.15:  # 15% chance to start moving
                self.is_moving = True
                # Random destination within ~500m
                self.target_pos = (
                    self.lat + random.uniform(-0.005, 0.005),
                    self.lon + random.uniform(-0.005, 0.005)
                )
                self.speed_mps = random.uniform(2.0, 8.0)
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
                move_distance = self.speed_mps * time_delta / 111000
                ratio = min(move_distance / distance, 1.0)
                self.lat += lat_diff * ratio
                self.lon += lon_diff * ratio

                # Vary speed slightly
                self.speed_mps += random.uniform(-0.5, 0.5)
                self.speed_mps = max(0, min(self.speed_mps, 10.0))

    def update_battery(self, time_delta: float):
        """Update battery level."""
        if self.is_moving:
            drain_rate = 0.015 * (self.speed_mps / 5.0)
            self.battery_pct -= drain_rate * (time_delta / 60)
        else:
            self.battery_pct -= 0.002 * (time_delta / 60)

        # Occasionally "charge"
        if not self.is_moving and random.random() < 0.01:
            self.battery_pct = min(100, self.battery_pct + random.uniform(5, 15))

        self.battery_pct = max(0, min(100, self.battery_pct))

    def generate_reading(self) -> dict:
        """Generate a telemetry reading."""
        # Simulate occasional impacts
        accel_g = random.uniform(0.8, 1.2)
        if self.is_moving and random.random() < 0.002:
            accel_g = random.uniform(3.5, 6.0)

        # Temperature varies
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
        """Advance simulation."""
        self.update_position(time_delta)
        self.update_battery(time_delta)


async def send_telemetry(reading: dict, api_url: str):
    """Send telemetry to API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{api_url}/ingest",
                json=reading,
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False


async def run_simulation(api_url: str, speed_multiplier: float = 1.0, duration: int = None):
    """Run simulation for existing devices."""

    # Use the seeded devices
    devices = [
        DeviceSimulator("bike-001", "New York"),
        DeviceSimulator("bike-002", "New York"),
        DeviceSimulator("bike-003", "New York"),
        DeviceSimulator("scooter-001", "San Francisco"),
        DeviceSimulator("scooter-002", "San Francisco"),
    ]

    print(f"\nSimulating {len(devices)} existing devices...")
    print(f"Speed multiplier: {speed_multiplier}x")
    print(f"API: {api_url}/ingest\n")

    update_interval = 5.0
    elapsed = 0
    readings_sent = 0
    start_time = datetime.now()

    try:
        while True:
            if duration and elapsed >= duration:
                break

            # Update all devices
            time_delta = update_interval * speed_multiplier
            for device in devices:
                device.step(time_delta)

            # Send telemetry
            tasks = []
            for device in devices:
                reading = device.generate_reading()
                tasks.append(send_telemetry(reading, api_url))

            results = await asyncio.gather(*tasks)
            successful = sum(results)
            readings_sent += successful

            elapsed += update_interval

            # Status
            avg_battery = sum(d.battery_pct for d in devices) / len(devices)
            moving_count = sum(1 for d in devices if d.is_moving)
            runtime = (datetime.now() - start_time).total_seconds()

            print(f"[{int(elapsed):3d}s] Sent {successful}/{len(devices)} | "
                  f"Moving: {moving_count} | Avg Battery: {avg_battery:5.1f}% | "
                  f"Total: {readings_sent:4d} | Rate: {readings_sent/runtime:.1f}/s")

            await asyncio.sleep(update_interval)

    except KeyboardInterrupt:
        print(f"\n\nStopped. Total readings: {readings_sent}")


def main():
    parser = argparse.ArgumentParser(description="FleetPulse Device Simulator")
    parser.add_argument("--api-url", default="http://localhost:8000/api/v1", help="API URL")
    parser.add_argument("--speed", type=float, default=1.0, help="Speed multiplier")
    parser.add_argument("--duration", type=int, help="Duration in seconds")

    args = parser.parse_args()
    asyncio.run(run_simulation(args.api_url, args.speed, args.duration))


if __name__ == "__main__":
    main()
