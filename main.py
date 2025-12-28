import sys
import time
from src.config import Config
from src.ingestion import IngestionPipeline
from src.rag_engine import RAGEngine

def main():
    # 1. Validación de Entorno
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Error de Configuración: {e}")
        sys.exit(1)

    # 2. Bucle Principal (Game Loop Pattern)
    while True:
        print("\n" + "="*40)
        print("      🧠 AZURE HYBRID RAG SYSTEM")
        print("="*40)
        print(" [1] 📄 Ingestar nuevo PDF")
        print(" [2] 💬 Iniciar Chat con la Base de Datos")
        print(" [3] 🚪 Salir")
        
        mode = input("\nSelecciona una opción (1-3): ").strip()

        # --- OPCIÓN 1: INGESTA ---
        if mode == "1":
            path = input("Ingresa la ruta del PDF (ej: data/document.pdf): ").strip()
            
            try:
                pipeline = IngestionPipeline()
                pipeline.process_pdf(path)
                input("\nPresiona ENTER para volver al menú...")
            except Exception as e:
                print(f"\n❌ Error durante la ingesta: {e}")
                time.sleep(2)

        # --- OPCIÓN 2: CHAT ---
        elif mode == "2":
            print("\n🔄 Inicializando Motor de Chat...")
            try:
                engine = RAGEngine()
                print("\n💬 --- CHAT INICIADO (Escribe 'salir' para volver) ---")
                
                while True:
                    q = input("\nUsuario 👤: ").strip()
                    
                    if q.lower() in ["salir", "exit", "menu"]:
                        print("Guardando sesión y volviendo al menú...")
                        break
                    
                    if not q: continue # Ignorar enters vacíos
                    
                    print("Bot 🤖: Pensando...", end="\r")
                    
                    # Llamada al cerebro
                    answer, sources = engine.chat(q)
                    
                    # Limpiar línea de "Pensando..."
                    print(" " * 20, end="\r")
                    
                    print(f"Bot 🤖: {answer}")
                    if sources:
                        print(f"📚 Fuentes: {list(set(sources))}")
                        
            except Exception as e:
                print(f"\n❌ Error crítico en el motor de chat: {e}")
                print("Tip: Verifica que el índice exista en Azure y tus claves sean correctas.")
                input("Presiona ENTER para continuar...")

        # --- OPCIÓN 3: SALIR ---
        elif mode == "3":
            print("👋 ¡Hasta luego!")
            sys.exit(0)
            
        else:
            print("⚠️ Opción no válida.")
            time.sleep(1)

if __name__ == "__main__":
    main()