n1, n2, n3, n4 = map(float, input().split())

mediaComPesos = ((n1 * 2) + (n2 * 3) + (n3 * 4) + (n4 *1)) / 10

if mediaComPesos >= 7.0:
    print("Media: %.1f\nAluno aprovado."% mediaComPesos)
elif mediaComPesos >=5.0 and mediaComPesos <= 6.9:
    notaExame = float(input())
    notaFinal = (notaExame + mediaComPesos) / 2
    if (notaFinal) >= 5:
        print("Media: %.1f\nAluno em exame.\nNota do exame: %.1f\nAluno aprovado.\nMedia final: %.1f" % (mediaComPesos, notaExame, notaFinal))
    else:
        print("Media: %.1f\nAluno em exame.\nNota do exame: %.1f\nAluno reprovado.\nMedia final: %.1f" % (mediaComPesos, notaExame, notaFinal))
else:
    print("Media: %.1f\nAluno reprovado."% mediaComPesos)

