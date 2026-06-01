import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk


PROJECT_DIR = Path(__file__).resolve().parent


class BotaoFlutuante:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Agente")

        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.92)
        self.root.overrideredirect(True)

        largura = 170
        altura = 64
        x = self.root.winfo_screenwidth() - largura - 20
        y = self.root.winfo_screenheight() - altura - 60
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")

        self.frame = tk.Frame(self.root, bg="#2d2d2d", bd=2, relief="raised")
        self.frame.pack(fill="both", expand=True)

        self.btn = tk.Button(
            self.frame,
            text="> INICIAR AGENTE",
            command=self.iniciar_agente,
            bg="#00a86b",
            fg="white",
            font=("Arial", 10, "bold"),
            border=0,
            cursor="hand2",
            activebackground="#007a4d",
            activeforeground="white",
        )
        self.btn.pack(fill="both", expand=True, padx=5, pady=5)

        self.status = tk.Label(
            self.frame,
            text="Pronto",
            bg="#2d2d2d",
            fg="#aaaaaa",
            font=("Arial", 7),
        )
        self.status.pack()

        self.frame.bind("<Button-1>", self.iniciar_arrasto)
        self.frame.bind("<B1-Motion>", self.arrastar)
        self.status.bind("<Button-1>", self.iniciar_arrasto)
        self.status.bind("<B1-Motion>", self.arrastar)

        self.btn_fechar = tk.Button(
            self.root,
            text="x",
            command=self.root.destroy,
            bg="#ff4444",
            fg="white",
            font=("Arial", 7, "bold"),
            border=0,
            cursor="hand2",
            width=2,
        )
        self.btn_fechar.place(x=largura - 18, y=2)

    def iniciar_arrasto(self, event):
        self.x = event.x
        self.y = event.y

    def arrastar(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def iniciar_agente(self):
        self.btn.config(
            text="PROCESSANDO...",
            bg="#ff8c00",
            state="disabled",
        )
        self.status.config(text="Capturando telas...")

        thread = threading.Thread(target=self.rodar_agente, daemon=True)
        thread.start()

    def rodar_agente(self):
        try:
            self.atualizar_status("Lendo documento...")
            resultado = subprocess.run(
                [sys.executable, str(PROJECT_DIR / "main.py")],
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=PROJECT_DIR,
            )

            if resultado.returncode == 0:
                self.atualizar_status("Concluido")
            else:
                self.atualizar_status("Erro")
                if resultado.stdout:
                    print(resultado.stdout)
                if resultado.stderr:
                    print(resultado.stderr, file=sys.stderr)
        except Exception as exc:
            self.atualizar_status(f"Erro: {exc}")
        finally:
            self.root.after(
                0,
                lambda: self.btn.config(
                    text="> INICIAR AGENTE",
                    bg="#00a86b",
                    state="normal",
                ),
            )

    def atualizar_status(self, texto):
        self.root.after(0, lambda: self.status.config(text=texto))

    def iniciar(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BotaoFlutuante()
    app.iniciar()
