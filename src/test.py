import sys
import os
import test2
from selenium import webdriver


def main():
	test2.test_fun()

	print("Hallo Verden!")
	print("Dir is: " + os.getcwd())
	print("Path to web driver:" + sys.argv[1])
	driver = webdriver.Chrome(sys.argv[1])



if __name__ == "__main__":
	main()

