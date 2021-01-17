<template>
  <nav class="">
    <div
      class="max-w-xl mx-auto text-blueGray-300 grid grid-flow-col items-center lg:gap-8 justify-center relative"
    >
      <NavbarButton to="/commands">Commands</NavbarButton>
      <NavbarButton to="/stats">Stats</NavbarButton>
      <NavbarButton to="/profiles">Profiles</NavbarButton>
      <NavbarButton to="/discord">Join Discord</NavbarButton>
    </div>
    <div
      class="w-4/5 border-b-1 mx-auto border-rose-50 border-opacity-20"
    ></div>
  </nav>
</template>

<script>
import NavbarButton from "./NavbarButton";
export default {
  name: "Navbar",
  components: { NavbarButton },
};
</script>