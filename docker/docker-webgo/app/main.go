package main

import (
    "fmt"
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    // Mapa para armazenar os IPs dos clientes
    clientIPs := make(map[string]bool)

    // Rota para exibir a lista de IPs dos clientes
    r.GET("/", func(c *gin.Context) {
        // Adiciona o IP do cliente à lista
        clientIP := c.ClientIP()
        clientIPs[clientIP] = true

        // Exibe a lista de IPs dos clientes
        c.Writer.WriteString("Lista de IPs dos clientes:\n")
        for ip := range clientIPs {
            c.Writer.WriteString(fmt.Sprintf("- %s\n", ip))
        }
    })

    // Inicia o servidor na porta 80
    http.ListenAndServe(":80", r)
}

