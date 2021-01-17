<template>
  <div>
    <LandingHeader class="border-b-1" style="border-color: #330d14" />
    <Section class="bg-theme border-b-1 border-blueGray-900">
      <Gallery :photoPulls="1234" />
    </Section>
    <Section class="bg-theme-alt">
      <Commands />
    </Section>
  </div>
</template>

<script>
import LandingHeader from "../components/LandingHeader.vue";
// import StatsBar from "../components/StatsBar.vue";
import Section from "../components/Section.vue";
import Gallery from "../components/Gallery/Gallery.vue";
import Commands from "../components/Commands/Commands.vue";

export default {
  components: { LandingHeader, Gallery, Section, Commands },
  name: "Home",
};
</script>
