#!/usr/bin/env python3
"""
AgroConnect Complete System Startup Script
Starts all backend APIs and the main frontend server
"""

import subprocess
import time
import os
import sys
import signal
import threading
from pathlib import Path

class AgroConnectSystem:
    def __init__(self):
        self.processes = []
        self.running = True
        
        # Define all services
        self.services = [
            {
                'name': 'Soil Analysis API',
                'script': 'simple_soil_server.py',
                'directory': 'soil_analysis',
                'port': 8001,
                'url': 'http://localhost:8001/health'
            },
            {
                'name': 'Crop Prediction API', 
                'script': 'simple_crop_server.py',
                'directory': 'crop_prediction',
                'port': 8002,
                'url': 'http://localhost:8002/health'
            },
            {
                'name': 'Market Analysis API',
                'script': 'simple_market_server.py', 
                'directory': 'market-analysis',
                'port': 8003,
                'url': 'http://localhost:8003/health'
            },
            {
                'name': 'Irrigation Calculator API',
                'script': 'simple_irrigation_server.py',
                'directory': 'irrigation_calculation', 
                'port': 8004,
                'url': 'http://localhost:8004/health'
            }
        ]
    
    def check_service_files(self):
        """Check if all service files exist"""
        print("🔍 Checking service files...")
        missing_services = []
        
        for service in self.services:
            script_path = Path(service['directory']) / service['script']
            if not script_path.exists():
                missing_services.append(f"{service['name']}: {script_path}")
        
        if missing_services:
            print("❌ Missing service files:")
            for service in missing_services:
                print(f"   - {service}")
            return False
        
        print("✅ All service files found")
        return True
    
    def start_service(self, service):
        """Start a single service"""
        try:
            script_path = Path(service['directory']) / service['script']
            
            print(f"🚀 Starting {service['name']}...")
            
            # Start the service
            process = subprocess.Popen(
                [sys.executable, service['script']],
                cwd=service['directory'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store process info
            service_info = {
                'name': service['name'],
                'process': process,
                'port': service['port'],
                'directory': service['directory']
            }
            self.processes.append(service_info)
            
            print(f"✅ {service['name']} started on port {service['port']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")
            return False
    
    def start_all_services(self):
        """Start all backend services"""
        print("🚀 Starting AgroConnect Backend Services...")
        print("=" * 60)
        
        success_count = 0
        for service in self.services:
            if self.start_service(service):
                success_count += 1
                time.sleep(2)  # Wait between service starts
        
        print(f"\n📊 Backend Services Status: {success_count}/{len(self.services)} started")
        
        if success_count == len(self.services):
            print("✅ All backend services started successfully!")
            return True
        else:
            print("⚠️ Some backend services failed to start")
            return False
    
    def start_main_server(self):
        """Start the main frontend server"""
        try:
            print("\n🌐 Starting Main Frontend Server...")
            
            # Start main server
            main_process = subprocess.Popen(
                [sys.executable, 'main_server.py', '8080'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store main server info
            main_info = {
                'name': 'Main Frontend Server',
                'process': main_process,
                'port': 8080,
                'directory': '.'
            }
            self.processes.append(main_info)
            
            print("✅ Main Frontend Server started on port 8080")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Main Frontend Server: {e}")
            return False
    
    def monitor_services(self):
        """Monitor all running services"""
        print("\n👀 Monitoring services...")
        
        while self.running:
            try:
                time.sleep(5)  # Check every 5 seconds
                
                for service_info in self.processes:
                    if service_info['process'].poll() is not None:
                        print(f"⚠️ {service_info['name']} has stopped unexpectedly")
                
            except KeyboardInterrupt:
                break
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        for service_info in self.processes:
            try:
                print(f"🔄 Stopping {service_info['name']}...")
                service_info['process'].terminate()
                
                # Wait for graceful shutdown
                try:
                    service_info['process'].wait(timeout=5)
                    print(f"✅ {service_info['name']} stopped")
                except subprocess.TimeoutExpired:
                    print(f"⚠️ Force killing {service_info['name']}...")
                    service_info['process'].kill()
                    service_info['process'].wait()
                    print(f"✅ {service_info['name']} force stopped")
                    
            except Exception as e:
                print(f"❌ Error stopping {service_info['name']}: {e}")
        
        print("✅ All services stopped")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n🔔 Received signal {signum}")
        self.stop_all_services()
        sys.exit(0)
    
    def run(self):
        """Run the complete AgroConnect system"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🌾 AgroConnect Complete System Startup")
        print("=" * 60)
        
        # Check files
        if not self.check_service_files():
            print("❌ Cannot start system - missing files")
            return False
        
        # Start backend services
        if not self.start_all_services():
            print("❌ Backend services failed to start")
            self.stop_all_services()
            return False
        
        # Wait a moment for services to initialize
        print("\n⏳ Waiting for services to initialize...")
        time.sleep(3)
        
        # Start main server
        if not self.start_main_server():
            print("❌ Main server failed to start")
            self.stop_all_services()
            return False
        
        # Display final status
        print("\n" + "=" * 60)
        print("🎉 AgroConnect System Started Successfully!")
        print("=" * 60)
        print("🌐 Frontend: http://localhost:8080")
        print("📱 Available Pages:")
        print("   🏠 Home:           http://localhost:8080/")
        print("   📊 Dashboard:      http://localhost:8080/dashboard")
        print("   🌱 Soil Analysis:  http://localhost:8080/soil")
        print("   💧 Irrigation:     http://localhost:8080/irrigation") 
        print("   📈 Market:         http://localhost:8080/market")
        print("   🌾 Crop:           http://localhost:8080/crop")
        print("\n⚡ Backend APIs:")
        for service in self.services:
            print(f"   {service['name']}: http://localhost:{service['port']}")
        print("=" * 60)
        print("🎯 Press Ctrl+C to stop all services")
        print("✅ All internal navigation links will work!")
        print()
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitor_services)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        return True

def main():
    """Main function"""
    system = AgroConnectSystem()
    
    try:
        success = system.run()
        if success:
            print("✅ AgroConnect system shut down successfully")
        else:
            print("❌ AgroConnect system failed to start")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        system.stop_all_services()
        sys.exit(1)

if __name__ == "__main__":
    main()
