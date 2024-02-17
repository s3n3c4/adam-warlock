palavra = "boneco"

letras_acertadas = ''

while True:
    entrada = input("Digite sua palvra: ")
    
    if len(entrada) > 1:
        print("Digite apenas uma letra.")
        continue


    if entrada in palavra:
        letras_acertadas += entrada

    
    palavra_formada = ''
    for letra_secreta in palavra:
        if letra_secreta in letras_acertadas:
                palavra_formada += letra_secreta
        else:
             palavra_formada += '*'
        print(palavra_formada)

    print('Palavra formada:', palavra_formada)


