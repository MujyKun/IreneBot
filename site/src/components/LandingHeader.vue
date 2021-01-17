<template>
  <main class="bg-theme flex flex-col overflow-hidden relative landing-section">
    <Navbar />
    <section
      class="max-w-7xl mx-auto flex flex-row justify-between lg:p-8 p-4 text-gray-300 h-full flex-1"
    >
      <div class="flex flex-col justify-center z-20">
        <transition appear enter-class="opacity-0" enter-to-class="opacity-100">
          <p class="uppercase font-semibold text-md" key="intr">
            — Introducing
          </p>
        </transition>
        <h1
          class="text-5xl lg:text-7xl font-black text-gray-300 mb-6 w-1/2"
          key="title"
        >
          A new Kpop experience on Discord
        </h1>
        <p
          class="lg:text-2xl text-xl max-w-md leading-relaxed font-regular mb-4"
        >
          A database of over <b>1.8 million</b> idol photos, kpop games, music
          radio, packaged with much more features.
        </p>
        <invite-button class="mb-4" />
        <p class="max-w-md mb-2 flex items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            width="18"
            height="18"
            class="fill-current mr-2"
          >
            <path fill="none" d="M0 0h24v24H0z" />
            <path
              d="M12 7a8 8 0 1 1 0 16 8 8 0 0 1 0-16zm0 3.5l-1.323 2.68-2.957.43 2.14 2.085-.505 2.946L12 17.25l2.645 1.39-.505-2.945 2.14-2.086-2.957-.43L12 10.5zm1-8.501L18 2v3l-1.363 1.138A9.935 9.935 0 0 0 13 5.049L13 2zm-2 0v3.05a9.935 9.935 0 0 0-3.636 1.088L6 5V2l5-.001z"
            />
          </svg>
          Top rated K-pop bot on top.gg according to users
        </p>
        <p class="flex items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            width="18"
            height="18"
            class="fill-current mr-2"
          >
            <path fill="none" d="M0 0h24v24H0z" />
            <path
              d="M12 2c5.52 0 10 4.48 10 10s-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2zm0 18c4.42 0 8-3.58 8-8s-3.58-8-8-8-8 3.58-8 8 3.58 8 8 8zm1-8h3l-4 4-4-4h3V8h2v4z"
            />
          </svg>
          Scroll down to learn more
        </p>
      </div>
      <StatsBar
        class="absolute bottom-0 left-0 right-0 z-20"
        :servers="5200"
        :users="500000"
        :commandUsage="1000000"
        :photos="1800000"
      />
    </section>
    <img
      class="z-0 bottom-0 left-0 top-0 w-full right-0 mx-auto absolute lg:opacity-70 opacity-40 max-h-full self-end object-cover h-full"
      style="object-position: 58% center"
      src="./wall.jpg"
    />
  </main>
</template>

<script>
import InviteButton from "./InviteButton.vue";
import Navbar from "./Navbar.vue";
import StatsBar from "./StatsBar";
export default {
  components: { InviteButton, StatsBar, Navbar },
  name: "LandingHeader",
  data() {
    return {
      visible: false,
    };
  },
  mounted() {
    setTimeout(() => {
      console.log("Mount");
      this.visible = true;
    }, 2000);
  },
};
</script>

<style scoped>
.landing-section {
  min-height: 100vh;
}
.list-item {
  display: inline-block;
  margin-right: 10px;
}
.list-enter-active,
.list-leave-active {
  transition: all 1s;
}
.list-enter, .list-leave-to /* .list-leave-active below version 2.1.8 */ {
  opacity: 0;
  transform: translateY(30px);
}
</style>