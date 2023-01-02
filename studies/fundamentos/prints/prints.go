package main

import "fmt"

func main() {
	fmt.Print("Mesma")
	fmt.Print(" linha.")

	fmt.Println(" Nova")
	fmt.Println("linha")

	x := 3.141516

	//fmt.Println("O valor de x é" + x)

	//float para string (conversão)
	xs := fmt.Sprint(x)
	fmt.Println("O valor de x é " + xs)
	fmt.Println("O valor de x é ", x)

	fmt.Printf("O valor de x é %.2f\n", x)
	fmt.Printf("O valor de x é %.2f.\n", x)
	fmt.Printf("O valor de x é %f\n", x)

	a := 1
	b := 1.9999
	c := false
	d := "opa"

	// d = inteiro; f = float; t = boolean; s = string
	fmt.Printf("\n%d %f %.1f %t %s", a, b, b, c, d)
	// O v imprime quase todos
	fmt.Printf("\n%v %v %.1v %v %v", a, b, b, c, d)

}
