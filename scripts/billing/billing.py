nubank = int(input("Digite aqui o que você precisar pagar para o NUBANK: \n"))
itau = int(input("Digite aqui o valor do Itaú: \n"))
luz = int(input("Quanto veio a luz esse mês?\n"))
aluguel = int(input("E o aluguel??\n"))

descontosMensais = (nubank + itau + aluguel + luz)
descontosMensaisImpostos = descontosMensais + 1696

ValorPensao = 0.2 #20%

salario = 5813 #BRUTO

pensao = int(salario) * ValorPensao #salario - 20%

salarioLiquido = salario + (- int(pensao) - descontosMensaisImpostos)

#salarioTotal = salarioLiquido - (descontosMensais)
print("O que você terá no fim do mês é: R$ %d" % salarioLiquido )

