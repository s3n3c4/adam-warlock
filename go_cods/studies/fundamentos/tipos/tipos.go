package main

import (
	"fmt"
	"math"
	"reflect"
)

func main() {
	// números inteiros
	fmt.Println(1, 2, 1000)
	fmt.Println("Literal inteiro é", reflect.TypeOf(32000))

	// sem sinal (só positivos)... uint8 uint16 uint32 uint64
	var b byte = 255
	fmt.Println("o byte é", reflect.TypeOf(b))

	// com sinal... int8 int16 in32 int64
	i1 := math.MaxInt64
	fmt.Println("O valor máximo do int é", i1)
	fmt.Println("O tipo de i1 é", reflect.TypeOf(i1))

	var i2 rune = 'a' // representa um mapemanto da tabela Unicode (int32)
	fmt.Println("o Rune é", reflect.TypeOf(i2))
	fmt.Println(i2)

	// números reais (float32, float64)

	var x float32 = 49.99
	fmt.Println("O tipo de x é", reflect.TypeOf(x))
	fmt.Println("o tipo do literal 49.99 é", reflect.TypeOf(49.99)) // float64

	// boolean
	bo := true
	fmt.Println("O tipo de bo é", reflect.TypeOf(bo))
	// exclamação nega a saída
	fmt.Println(!bo)

	// string com múltiplas linhas
	s2 := `Olá
	meu
	nome
	é
	Leo`
	fmt.Println("O tamanho da string é", len(s2))

	// char???
	char := 'a'
	fmt.Println("O tipo de char é", reflect.TypeOf(char))
	fmt.Println(char)

}
