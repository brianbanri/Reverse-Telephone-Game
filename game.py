import pyaudio
import wave
from playsound import playsound



FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output0" #add.wav in playback
audio = pyaudio.PyAudio()
FILE_NUM = 0

def titleScreen():

	print("\nWelcome to The Reverse Telephone Game!\n")
	print("Type \"Start Local Game\" to start a new game on this device")
	print("Type \"Host Game\" to host a new game")
	print("Type \"Join Game\" to join an existing game")

	user_input = input()
	print()

	if user_input.lower() == "host game":
		host_game(audioDevice)
	elif user_input.lower() == "join game":
		join_game(audioDevice)
	elif user_input.lower() == "start local game":
		start_local_game(audioDevice)

def start_local_game(audioDevice):
	print("starting local game...\n")
	print("Enter number of players:")
	player_count = int(input())
	print()
	if(player_count < 4):
		print("You need 4 or more players to play this game.")
		quit() #calling the title screen here leads to an error once the main game is completed with optimum players, so I chose to quit instead.

	start_game(player_count, audioDevice)

def host_game(audioDevice):
	print("hosting game...\n")

def join_game(audioDevice):
	print("joining game...\n")

def start_game(player_count, audioDevice):
	round_counter = 0

	print("Game starting with %d players...\n" %player_count)

	player_names = []
	for i in range(player_count):
		print("Enter name for player", i+1, ":")
		player_names.append(input())
		print()

	#Start Round 1
	round_counter += 1
	sentence = round1(player_names)
	#End Round 1

	#Start Round 2
	round_counter += 1
	audio = round2(sentence, player_names)
	#End Round 2

	#Start Round 3
	#But we will be alternating between reverse and interpret rounds now 
	round_counter += 1
	while round_counter < player_count:
		if round_counter % 2 == 1:
			audio = reverse_round(player_names, round_counter - 1)
		else:
			audio = interpret_round(player_names, round_counter - 1)
		round_counter += 1

	#Start Round player_count
	if player_count % 2 == 0:
		# Extra reverse for even number of player games
		reverse_audio()

	finalGuess = guess_round(player_names, round_counter - 1) #store for the recap round
	with open('finalGuess.txt', 'w') as f: #store for recap round
		f.write(finalGuess)

	spectate(sentence, finalGuess, player_count, player_names)
	
def round1(player_names):
	prompt_player(player_names, 0)
	print("%s enter a word:" %player_names[0])
	sentence = input() 
	with open('initWord.txt', 'w') as f: #store for recap round
		f.write(sentence)
	print()

	return sentence

def round2(sentence, player_names):
	prompt_player(player_names, 1)
	print("Record yourself saying this word.")
	print(sentence)
	print()
	print("Ready to record?")
	ready_check(player_names, 1)
	record_audio()
	print()

def reverse_round(player_names, i):
	prompt_player(player_names, i)
	print("Record yourself saying repeating the word you will hear.")
	ready_check(player_names, i)
	reverse_audio()
	play_audio()
	print("Ready to record? [You can enter Replay to re-hear the audio]")
	if(replay_check() == 1): 
		play_audio()	#CHECKING IF USER WANTS AUDIO REPLAYED
	ready_check(player_names, i)
	record_audio()
	print()
	

def interpret_round(player_names, i):
	prompt_player(player_names, i)
	print("Record your best guess of what the original word was after hearing the reversed audio.")
	ready_check(player_names, i)
	reverse_audio()
	play_audio()
	print("Ready to record? [You can enter Replay to re-hear the audio]")
	if(replay_check() == 1): 
		play_audio()	#CHECKING IF USER WANTS AUDIO REPLAYED
	ready_check(player_names, i) #check for replay option, make new ready checker for any listening calls
	record_audio()
	print()

def guess_round(player_names, i):
	prompt_player(player_names, i)
	print("Type your best guess of what the original word was after hearing audio.")
	print("Ready to hear the recording?")
	ready_check(player_names, i)
	play_audio()
	print("Would you like to hear it again? [Only 1 Replay Allowed]")
	if(replay_check() == 1): 
		play_audio()	#CHECKING IF USER WANTS AUDIO REPLAYED
	print("Type your answer: ")
	sentence = input()
	
	return sentence

#Helper to play specific file at any given moment
def give_audio(file):
	wf = wave.open(file, 'rb')

	stream = audio.open(
	    format = audio.get_format_from_width(wf.getsampwidth()),
	    channels = wf.getnchannels(),
	    rate = wf.getframerate(),
	    output = True
	)

	data = wf.readframes(CHUNK)
	while len(data) > 0:
	    stream.write(data)
	    data = wf.readframes(CHUNK)

	stream.close()

#Function to show the proceedings of the game
def spectate(beginning, end, player_num, players): 
	print("\nHere is the playback, hope you had fun! ") #Placeholder until I get the functionality of the method.
	#LOOP THROUGH PLAYERS AND THEIR INPUTS ONE BY ONE 
	print("Press enter to proceed")
	input()
	for i in range(player_num):
		if (i==0):
			print("%s entered:" %players[i], beginning)
		
		else:
			if (i==player_num-1):
				print("Press enter to proceed")
				input()
				print("%s thought the original word was: " %players[i], end)
				if(beginning.lower() == end.lower()):
					print("And it was indeed ' %s '. Good Job!" %beginning)
				else:
					print("But it really was: ' %s '! \n" %beginning)
			else:
				print("Press enter to proceed")
				input()
				print("%s said:" %players[i])
				give_audio("output"+str(i)+".wav")



def prompt_player(player_names, i):
	print("Pass the device to %s...\n" %player_names[i])
	ready_check(player_names, i)

def replay_check():
	if(input()=="replay"): return 1
	else: return 0


def ready_check(player_names, i):
	print("%s type \"ready\" to continue..." %player_names[i])
	while(input() != "ready"):
		pass
	print()

def record_audio():

	stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,input_device_index = audioDevice,
                frames_per_buffer=CHUNK)
	print ("recording started")
	Recordframes = []
	 
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    Recordframes.append(data)
	print ("recording stopped")
	 
	stream.stop_stream()
	stream.close()

	global FILE_NUM 
	FILE_NUM += 1
	global WAVE_OUTPUT_FILENAME 
	WAVE_OUTPUT_FILENAME = WAVE_OUTPUT_FILENAME[:-1]
	WAVE_OUTPUT_FILENAME += str(FILE_NUM)
	waveFile = wave.open(WAVE_OUTPUT_FILENAME+".wav", 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(Recordframes))
	waveFile.close()

def reverse_audio():
	wf = wave.open(WAVE_OUTPUT_FILENAME+".wav", 'rb')

	stream = audio.open(
	    format = audio.get_format_from_width(wf.getsampwidth()),
	    channels = wf.getnchannels(),
	    rate = wf.getframerate(),
	    output = True
	)

	recording = []
	data = wf.readframes(CHUNK)
	while len(data) > 0:
	    data = wf.readframes(CHUNK)
	    recording.append(data)

	recording = recording[::-1]
	print("PLAYING: ",WAVE_OUTPUT_FILENAME)
	waveFile = wave.open(WAVE_OUTPUT_FILENAME+".wav", 'wb') #concatenate file number here
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(recording))
	waveFile.close()

	stream.close()

def play_audio():
	wf = wave.open(WAVE_OUTPUT_FILENAME+".wav", 'rb')

	stream = audio.open(
	    format = audio.get_format_from_width(wf.getsampwidth()),
	    channels = wf.getnchannels(),
	    rate = wf.getframerate(),
	    output = True
	)

	data = wf.readframes(CHUNK)
	while len(data) > 0:
	    stream.write(data)
	    data = wf.readframes(CHUNK)

	stream.close()

def setupAudioDevice():
	print("----------------------record device list---------------------")
	info = audio.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	for i in range(0, numdevices):
	        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
	            print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

	print("-------------------------------------------------------------")

	index = int(input())
	print("recording via index "+str(index))

	return index



def main():
	titleScreen()

if __name__ == "__main__":

	audioDevice = setupAudioDevice();
	main()

#test