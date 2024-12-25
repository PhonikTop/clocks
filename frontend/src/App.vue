<template>
  <div class="logo">
    <h2>Часики<span class="tick-animated">:</span>тикают</h2>
  </div>
  <router-view/>
</template>

<style>
.logo {
  text-align: center;
  padding: 20px;
  display: block;
}

.logo h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0;
}

.logo .tick {
  color: #6B6B6B;
}

@keyframes blink {
  0%, 100% { opacity: 1; } /* Элемент виден */
  50% { opacity: 0; }      /* Элемент мерцает и становится невидимым! */
}

.tick-animated {
  animation: blink 1.3s ease-in-out infinite; /* Позволяет тексту постоянно мигать */
}
</style>
