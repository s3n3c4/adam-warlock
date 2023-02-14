package main

import (
	"fmt"
	"math"
)

func main() {
	const PI float64 = 3.1415
	var raio = 3.2 // tiop (float64) inferido pelo compilador

	//forma redudiza de criar uma var
	area := PI * math.Pow(raio, 2)
	fmt.Println("A área de circunferência é", area)

	const (
		a = 1
		b = 2
	)

	var (
		c = 3
		d = 4
	)

	fmt.Println(a, b, c, d)

	var e, f bool = true, false
	fmt.Println(e, f)

	// Maneira de declrar sem ter que especificar o tipo dela
	g, h, i := 2, false, "eeeeeeepa!"
	fmt.Println(g, h, i)

}
