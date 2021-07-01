<template>
  <nav class="">
    <div
      class="max-w-xl mx-auto text-blueGray-300 grid grid-flow-col items-center lg:gap-8 justify-center relative"
    >
      
      <NavbarButton to="/">Home</NavbarButton>
      <NavbarButton to="/commands">Commands</NavbarButton>
      <NavbarButton to="/stats">Stats</NavbarButton>
      <NavbarButton to="/profiles">Profiles</NavbarButton>
      <NavbarButton to="/discord">Join Discord</NavbarButton>

      <!--
      All Buttons appear faded out in the nav bar and
      the a tag is not working. 
      
      <div
        class="ml-96">
          <PatreonButton></PatreonButton>
      </div>
      !--> 
    </div>

    <div
      class="w-4/5 border-b-1 mx-auto border-rose-50 border-opacity-20"
    ></div>
  </nav>
</template>

<script>
import NavbarButton from "./NavbarButton";
import PatreonButton from "./PatreonButton.vue";

export default {
  name: "Navbar",
  components: { NavbarButton, PatreonButton},
};
</script>