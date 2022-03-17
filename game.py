def titleScreen():
	print("\nWelcome to The Reverse Telephone Game!\n")
	print("Type \"Start Local Game\" to start a new game on this device")
	print("Type \"Host Game\" to host a new game")
	print("Type \"Join Game\" to join an existing game")

	user_input = input()
	print()

	if user_input.lower() == "host game":
		host_game()
	elif user_input.lower() == "join game":
		join_game()
	elif user_input.lower() == "start local game":
		start_local_game()

def start_local_game():
	print("starting local game...\n")
	print("Enter number of players:")
	player_count = int(input())
	print()

	start_game(player_count)

def host_game():
	print("hosting game...\n")

def join_game():
	print("joining game...\n")

def start_game(player_count):
	round_counter = 0

	print("Game starting with %d players...\n" %player_count)

	player_names = []
	for i in range(player_count):
		print("Enter name for player", i, ":")
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
	round_counter += 1
	while round_counter < player_count:
		if round_counter % 2 == 1:
			audio = reverse_round(audio, player_names, round_counter - 1)
		else:
			audio = interpret_round(audio, player_names, round_counter - 1)
		round_counter += 1

	#Start Round player_count
	if player_count % 2 == 0:
		# Extra reverse for even number of player games
		reverse_audio()

	guess_round()
	
def round1(player_names):
	prompt_player(player_names, 0)
	print("%s enter a sentence:" %player_names[0])
	sentence = input()

	return sentence

def round2(sentence, player_names):
	prompt_player(player_names, 1)
	print("Record yourself saying this sentence(but actually just retype it): ")
	print(sentence)
	return record_audio()

def reverse_round(audio, player_names, i):
	prompt_player(player_names, i)
	audio = reverse_audio(audio)
	print("Record yourself saying repeating the sentence you will hear(but actually just retype it): ")
	ready_check(player_names, i)
	play_audio(audio)
	return record_audio()
	

def interpret_round(audio, player_names, i):
	prompt_player(player_names, i)
	audio = reverse_audio(audio)
	print("Record your best guess of what the original sentence was after hearing the reversed audio(but actually just retype it): ")
	ready_check(player_names, i)
	play_audio(audio)
	return record_audio()

def guess_round():
	pass

def prompt_player(player_names, i):
	print("Pass the device to %s...\n" %player_names[i])
	ready_check(player_names, i)

def ready_check(player_names, i):
	print("%s type \"ready\" to continue..." %player_names[i])
	while(input() != "ready"):
		pass
	print()

def record_audio():
	return input()

def reverse_audio(audio):
	return audio[::-1]

def play_audio(audio):
	print(audio)

def main():
	titleScreen()


if __name__ == "__main__":
	main()
