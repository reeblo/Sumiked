#!/usr/bin/env python3
"""
Script alternativo simple para configurar la base de datos
"""
from init_database import init_database

if __name__ == '__main__':
    print("🔧 Configurando base de datos de Sumiked...")
    init_database()
    print("✅ Configuración completada")