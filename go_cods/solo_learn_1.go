package main

import "fmt"

func main() {
	for v := range m {
		fmt.Print("Digite aqui o seu numero: ")
		fmt.Scanf("%v", &v)
		fmt.Print("Hello", v)

	}

}
