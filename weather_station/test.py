
import sys
import time
from threading import Event
import signal 

exit = Event()

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    print(f'received kill signal {signum}, exiting')
    self.kill_now = True

k = GracefulKiller()

def main():
    while not exit.is_set():
        print('sleeping for 10...')
        time.sleep(10)
        print('waiting for 10...')
        exit.wait(10)
    else:
        print('exiting!')
        sys.exit(0)

def quit(signum, _frame):
    print(f'received kill signal {signum}, exiting')
    exit.set()

if __name__ == '__main__':
    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig), quit);

    main()
