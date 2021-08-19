<template>
  <div>
     <Navbar />
  </div>
    <img
    class="z-0 bottom-0 left-0 top-0 w-full right-0 mx-auto absolute lg:opacity-70 opacity-40 max-h-full self-end object-cover h-full"
    style="object-position: 58% center"
    src="./../components/wall.jpg"
    />
</template>

<script>
import Navbar from "../components/Navbar.vue";

export default {
  components: { Navbar },
  name: "Stats",
};
</script>
