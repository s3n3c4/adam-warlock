// This example requires the Chilkat API to have been previously unlocked.
// See Global Unlock Sample for sample code.
package main

import "fmt"

// The mailman object is used for sending and receiving email.
func main() {

	mailman := chilkat.NewMailMan()

	// Set the SMTP server.  Perhaps it is the local machine.
	mailman.SetSmtpHost("localhost")
	// Or perhaps it's a particular computer on the local network:
	mailman.SetSmtpHost("192.168.1.123")
	// Or provide a local domain that resolves to an IP address on the local network:
	mailman.SetSmtpHost("smtp.globoi.com")

	// Set the SmtpAuthMethod property = "NONE"
	mailman.SetSmtpAuthMethod("NONE")

	// Set the SMTP login/password (this may be omitted given no authentication will take place)
	// mailman.SmtpUsername = "myUsername";
	// mailman.SmtpPassword = "myPassword";

	// Create a new email object
	email := chilkat.NewEmail()

	email.SetSubject("This is a test")
	email.SetBody("This is a test")
	email.SetFrom("Chilkat Support <support@chilkatsoft.com>")
	success := email.AddTo("Chilkat Admin", "admin@chilkatsoft.com")
	// To add more recipients, call AddTo, AddCC, or AddBcc once per recipient.

	// Call SendEmail to connect to the SMTP server and send.
	// The connection (i.e. session) to the SMTP server remains
	// open so that subsequent SendEmail calls may use the
	// same connection.
	success = mailman.SendEmail(email)
	if success != true {
		fmt.Println(mailman.LastErrorText())
		mailman.DisposeMailMan()
		email.DisposeEmail()
		return
	}

	// Some SMTP servers do not actually send the email until
	// the connection is closed.  In these cases, it is necessary to
	// call CloseSmtpConnection for the mail to be  sent.
	// Most SMTP servers send the email immediately, and it is
	// not required to close the connection.  We'll close it here
	// for the example:
	success = mailman.CloseSmtpConnection()
	if success != true {
		fmt.Println("Connection to SMTP server not closed cleanly.")

	}

	fmt.Println("Mail Sent!")

	mailman.DisposeMailMan()
	email.DisposeEmail()

}
