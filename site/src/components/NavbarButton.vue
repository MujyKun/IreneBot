<template>
  <a
    class="lg:py-6 text-base py-4 px-2 font-semibold z-20 hover:text-blueGray-100"
  >
    <router-link :to="to"><slot></slot></router-link>
  </a>
</template>
<script>
export default {
  name: "NavbarButton",
  props: {
    to: String,
  },
};
</script>