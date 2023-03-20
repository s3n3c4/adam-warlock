package main

import "log"

func main() { 
	myVar := "dog"

	switch myVar { 
	case "cat":
		log.Println("cat is set to cat")

	case "dog":
		log.Println("cat is set to dog")

	case "fish":
		log.Println("cat is set to fish")

	default:
		log.Println("cat is something else")

	}
}
