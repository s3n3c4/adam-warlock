package main

import (
	"fmt"
	"net/smtp"
)

func main() {

	// Sender data.
	from := "allan.cordeiro@globo.com"
	//password := "Seneca@5120"

	// Receiver email address.
	to := []string{
		"allan.cordeiro@g.globo",
	}

	// smtp server configuration.
	smtpHost := "smtp.globoi.com"
	smtpPort := "25"

	// Message.
	message := []byte("Outro teste!")

	// Authentication.
	//auth := smtp.PlainAuth(from, smtpHost)

	// Sending email.
	err := smtp.SendMail(smtpHost+":"+smtpPort, from, to, message)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println("Email Sent Successfully!")
}
