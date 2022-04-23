import pyaudio
import click
import wave
from colorama import Fore, Back
from colorama import init as colorama_init
from art import text2art
import os
from tqdm import trange
from time import sleep

os.system('mode con: cols=170 lines=40')
click.clear()
colorama_init(autoreset=True)
Art = text2art("                                               WELCOME", font='big')
print(f"{Fore.LIGHTGREEN_EX}{Art}")

def waitingBar():
    sleep(0.1)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "recordedFile0" #add.wav in playback
audio = pyaudio.PyAudio()
FILE_NUM = 0

def titleScreen():
	titleScreen = text2art("                       WELCOME                   TO \nREVERSE TELEPHONE GAME", font='big')
	print(f"{Fore.LIGHTGREEN_EX}{titleScreen}")
	start_local = "Type \"Start Local Game\" to start a new game on this device"
	host_game_text = "Type \"Host Game\" to host a new game"
	join_game_text = "Type \"Join Game\" to join an existing game"
	print(f"{Fore.LIGHTRED_EX}{start_local}")
	print(f"{Fore.LIGHTRED_EX}{host_game_text}")
	print(f"{Fore.LIGHTRED_EX}{join_game_text}")


	user_input = input()
	print()

	if user_input.lower() == "host game":
		host_game(audioDevice)
	elif user_input.lower() == "join game":
		join_game(audioDevice)
	elif user_input.lower() == "start local game":
		start_local_game(audioDevice)

def start_local_game(audioDevice):
	text_1 = "Starting Local Game...\n"
	print(f"{Fore.LIGHTRED_EX}{text_1}")
	for i in trange(10):
		waitingBar()
	text_2 = "\nEnter number of players: (4 MINIMUM)"
	print(f"{Fore.LIGHTRED_EX}{text_2}")
	player_count = int(input())
	print()
	if(player_count < 4):
		text_3 = "You need 4 or more players to play this game."
		print(f"{Fore.LIGHTRED_EX}{text_3}")
		quit() #calling the title screen here leads to an error once the main game is completed with optimum players, so I chose to quit instead.

	start_game(player_count, audioDevice)

def host_game(audioDevice):
	print("hosting game...\n")

def join_game(audioDevice):
	print("joining game...\n")

def start_game(player_count, audioDevice):
	click.clear()
	round_counter = 0
	setup_phase = text2art("SETUP", font='small')
	print(f"{Fore.LIGHTGREEN_EX}{setup_phase}")

	print(Fore.LIGHTRED_EX + "Game starting with %d players...\n" %player_count)

	player_names = []
	for i in range(player_count):
		print(Fore.LIGHTRED_EX + "Enter name for player", i+1, ":")
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
	
def round1(player_names):
	prompt_player(player_names, 0)
	print(Fore.LIGHTRED_EX + "%s enter a sentence:" %player_names[0])
	sentence = input() 
	with open('initWord.txt', 'w') as f: #store for recap round
		f.write(sentence)
	print()

	return sentence

def round2(sentence, player_names):
	prompt_player(player_names, 1)
	print(Fore.LIGHTRED_EX + "Record yourself saying this sentence (in green).\n")
	print(Fore.LIGHTGREEN_EX + sentence)
	sleep(5)
	print()
	print(Fore.LIGHTRED_EX + "Ready to record?")
	ready_check(player_names, 1)
	record_audio()
	print()

def reverse_round(player_names, i):
	prompt_player(player_names, i)
	print(Fore.LIGHTRED_EX + "Record yourself saying repeating the sentence you will hear.")
	ready_check(player_names, i)
	reverse_audio()
	play_audio()
	print(Fore.LIGHTRED_EX + "Ready to record?")
	ready_check(player_names, i)
	record_audio()
	print()
	

def interpret_round(player_names, i):
	prompt_player(player_names, i)
	print(Fore.LIGHTRED_EX + "Record your best guess of what the original sentence was after hearing the reversed audio.")
	ready_check(player_names, i)
	reverse_audio()
	play_audio()
	print(Fore.LIGHTRED_EX + "Ready to record?")
	ready_check(player_names, i)
	record_audio()
	print()

def guess_round(player_names, i):
	prompt_player(player_names, i)
	print(Fore.LIGHTRED_EX + "Type your best guess of what the original sentence was after hearing audio.")
	print(Fore.LIGHTRED_EX + "Ready to hear the recording?")
	ready_check(player_names, i)
	play_audio()
	print(Fore.LIGHTRED_EX + "Type your answer: ")
	sentence = input()
	
	return sentence

#Function to show the proceedings of the game
def spectate_round():
	print(Fore.LIGHTRED_EX + "Here is the playback, hope you had fun! ") #Placeholder until I get the functionality of the method.
	#POSSIBLY LOOP THROUGH PLAYERS AND THEIR INPUTS ONE BY ONE

def prompt_player(player_names, i):
	click.clear()
	prompt_player_text = text2art(player_names[i], font='small')
	print(f"{Fore.LIGHTGREEN_EX}{prompt_player_text}")
	print(Fore.LIGHTRED_EX + "Pass the device to %s...\n" %player_names[i])
	ready_check(player_names, i)

def ready_check(player_names, i):
	print(Fore.LIGHTRED_EX + "%s type \"ready\" to continue..." %player_names[i])
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
	print(Fore.LIGHTGREEN_EX + "PLAYING: ",WAVE_OUTPUT_FILENAME)
	print()
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
	print("\t\t\t\t\t\t----------------------RECORDING DEVICE LIST---------------------")
	info = audio.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	for i in range(0, numdevices):
	        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
	            print("\t\t\t\t\t\tInput Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

	print("\t\t\t\t\t\t----------------------------------------------------------------")

	index = click.prompt(Fore.LIGHTRED_EX + 'Choose your audio device', type=int)
	print("recording via index "+str(index))
	click.clear()
	return index



def main():
	titleScreen()

if __name__ == "__main__":

	audioDevice = setupAudioDevice();
	main()

#test