import board
import digitalio
import storage
 
switch = digitalio.DigitalInOut(board.D7)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP
 
# Mount the storage based on the on-board switch
# Switch position right for REPL/Android app
# Switch position left for normal USB Storage
storage.remount("/", switch.value)
    
