import threading
import queue
import time
import random

TIMEOUT = 0.6        
LOCK_PRINT = threading.Lock()
INICIO = time.time()


def log(msg):
    with LOCK_PRINT:
        t = time.time() - INICIO
        print(f"  [t={t:4.2f}s] {msg}")


class Processo(threading.Thread):
    def __init__(self, pid, todos_processos, ativos):
        super().__init__(daemon=True, name=f"P{pid}")
        self.pid = pid
        self.todos = todos_processos     
        self.ativos = ativos           
        self.caixa_entrada = queue.Queue()
        self.coordenador = None
        self.em_eleicao = threading.Event()
        self.recebeu_ok = threading.Event()
        self.encerrar = threading.Event()
        self.lock_estado = threading.Lock()

    def enviar(self, destino_pid, tipo, remetente=None):
        remetente = self.pid if remetente is None else remetente
        if destino_pid in self.ativos and destino_pid in self.todos:
            time.sleep(random.uniform(0.01, 0.05))  
            self.todos[destino_pid].caixa_entrada.put((tipo, remetente))

    def iniciar_eleicao(self):
        with self.lock_estado:
            if self.em_eleicao.is_set():
                return  
            self.em_eleicao.set()
            self.recebeu_ok.clear()

        superiores = [p for p in self.todos if p > self.pid and p in self.ativos]
        if not superiores:
            with self.lock_estado:
                self.vencer_eleicao()
            return

        log(f"P{self.pid} inicia ELEIÇÃO → envia ELECTION para {['P'+str(s) for s in superiores]}")
        for p in superiores:
            self.enviar(p, "ELECTION")

        recebeu = self.recebeu_ok.wait(timeout=TIMEOUT)
        with self.lock_estado:
            if not self.em_eleicao.is_set():
                return  
            if not recebeu:
                self.vencer_eleicao()
            else:
                log(f"P{self.pid} recebeu OK de processo superior → encerra participação, aguarda COORDINATOR")
                self.em_eleicao.clear()

    def vencer_eleicao(self):
        if self.coordenador == self.pid:
            return 
        self.coordenador = self.pid
        self.em_eleicao.clear()
        log(f"P{self.pid} não recebeu resposta de nenhum superior → VENCE a eleição")
        log(f"P{self.pid} se torna o novo COORDENADOR")
        for p in self.todos:
            if p != self.pid:
                self.enviar(p, "COORDINATOR")

    def run(self):
        while not self.encerrar.is_set():
            try:
                tipo, remetente = self.caixa_entrada.get(timeout=0.2)
            except queue.Empty:
                continue

            if tipo == "ELECTION":
                if self.coordenador == self.pid:
                    log(f"P{self.pid} ← ELECTION ← P{remetente}  (já sou coordenador, apenas confirmo OK)")
                    self.enviar(remetente, "OK")
                    self.enviar(remetente, "COORDINATOR")
                    continue
                log(f"P{self.pid} ← ELECTION ← P{remetente}")
                self.enviar(remetente, "OK")
                log(f"P{self.pid} → OK → P{remetente}  (assume a eleição)")
                threading.Thread(target=self.iniciar_eleicao, daemon=True).start()

            elif tipo == "OK":
                log(f"P{self.pid} ← OK ← P{remetente}")
                self.recebeu_ok.set()

            elif tipo == "COORDINATOR":
                self.coordenador = remetente
                self.em_eleicao.clear()
                log(f"P{self.pid} ← COORDINATOR ← P{remetente}  (novo coordenador reconhecido)")


def main():
    N = 12
    pids = list(range(N))                   
    coordenador_inicial = N - 1             

    candidatos_inativo_extra = [p for p in pids if p != coordenador_inicial]
    tem_inativo_extra = random.choice([True, False])
    inativo_extra = random.choice(candidatos_inativo_extra) if tem_inativo_extra else None

    inativos_iniciais = {coordenador_inicial}
    if inativo_extra is not None:
        inativos_iniciais.add(inativo_extra)
    ativos = set(pids) - inativos_iniciais

    detector = random.choice(list(ativos))

    print("=" * 68)
    print("  Algoritmo Bully (com threads) — Eleição de Coordenador")
    print(f"  Processos: P0 a P{N-1}   |   Coordenador inicial fixo: P{coordenador_inicial}")
    print(f"  Cenário sorteado nesta execução:")
    if inativo_extra is not None:
        print(f"    Processo extra também inativo desde o início: P{inativo_extra}")
    else:
        print(f"    Nenhum processo extra inativo (apenas o coordenador caiu)")
    print(f"    Detector da falha (sorteado): P{detector}")
    print("=" * 68)
    print()

    processos = {}
    for pid in pids:
        processos[pid] = Processo(pid, processos, ativos)

    for p in processos.values():
        p.start()

    log(f"Estado inicial: P{coordenador_inicial} (coordenador) FALHOU")
    if inativo_extra is not None:
        log(f"P{inativo_extra} também está inativo desde o início")
    log(f"Processos ativos: {sorted(ativos)}")
    print()

    log(f"P{detector} detecta que o coordenador não está respondendo")
    threading.Thread(target=processos[detector].iniciar_eleicao, daemon=True).start()

    time.sleep(3.5)

    for p in processos.values():
        p.encerrar.set()
    for p in processos.values():
        p.join(timeout=1)

    print()
    print("=" * 68)
    print("  RESULTADO FINAL — coordenador reconhecido por cada processo:")
    for pid in sorted(ativos):
        print(f"    P{pid}.coordenador = P{processos[pid].coordenador}")
    print("=" * 68)


if __name__ == "__main__":
    main()
