<template>
  <a href="http://api.irenebot.com/invite/">
    <button 
      class="flex items-center rounded overflow-hidden bg-blurple-dark w-min transition-shadow shadow-lg"
      role="button">
    <span class="p-3 bg-blurple">
      <DiscordIcon class="discord-icon w-6" />
    </span>
    <p class="text-blueGray-200 font-semibold px-6 whitespace-nowrap">
      Invite Irene
    </p>
    </button>
  </a>
</template>

<script>
import DiscordIcon from "./svg/Discord";
export default {
  components: { DiscordIcon },
  name: "InviteButton"
};
</script>

<style scoped>
.discord-icon {
  fill: rgb(219, 219, 219);
}
</style>