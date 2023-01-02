package main

import (
	"fmt"
	"strconv"
)

func main() {
	x := 2.4
	y := 2
	// Para converter, precisa por o float64
	fmt.Println(x / float64(y))

	nota := 6.9
	notaFinal := int(nota)
	fmt.Println(notaFinal)

	// cuidado... ASCI!
	fmt.Println("Teste " + string(97))

	// int para string
	fmt.Println("Teste " + strconv.Itoa(123))

	// string para int
	num, _ := strconv.Atoi("123")
	fmt.Println(num - 122)

	b, _ := strconv.ParseBool("0.2")
	if b {
		fmt.Println("Verdadeiro")
	}
}
