import os

volumes_path = "/Volumes/Filme+Backups/Content "
again_path = "./Utils/titles_again.txt"
scrape_again = ""

for index in range(1, 8):

	file_path = volumes_path + str(index) + "/"
	files = os.listdir(file_path)

	counter = 0
	for file in files:
		file_size = int(os.stat(file_path + file).st_size) # in bytes
		if file_size < 2000:
			scrape_again += file + "\n"
			counter += 1

with open(again_path, "w") as file:
	file.write(scrape_again)