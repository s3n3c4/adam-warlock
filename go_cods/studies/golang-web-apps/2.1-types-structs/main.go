package main

import (
	"log"
	"time"
)

type User struct {
	FirstName   string
	LastName    string
	PhoneNumber string
	Age         int
	Birthday    time.Time
}

func main() {
	user := User{
		FirstName: "Marcos",
		LastName:  "Aurélio",
	}

	log.Println(user.FirstName, user.LastName, "Birthday: ", user.Birthday)

}
