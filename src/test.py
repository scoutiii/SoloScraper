import sys
import os
from selenium import webdriver


def main():
	

	print("Hallo Verden!")
	print("Dir is: " + os.getcwd())
	print("Path to web driver:" + sys.argv[1])
	driver = webdriver.Chrome(sys.argv[1])



if __name__ == "__main__":
	main()

