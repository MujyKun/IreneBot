<template>
  <a href="http://api.irenebot.com/patreon/">
    <button 
      class="flex items-center rounded overflow-hidden bg-red-600 bg-opacity-90 w-min transition-shadow shadow-lg"
      role="button">
    <span class="p-3 bg-gray-200">
      <PatreonIcon class="patreon-icon w-6" />
    </span>
    <p class="text-blueGray-200 font-semibold px-6 whitespace-nowrap">
      Become A Patron!
    </p>
    </button>
  </a>
</template>

<script>
import PatreonIcon from "./svg/Patreon";
export default {
  components: { PatreonIcon },
  name: "PatreonButton"
};
</script>