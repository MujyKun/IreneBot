<template>
  <div>
    <LandingHeader class="border-b-1" style="border-color: #330d14" />
    <Section class="bg-theme border-b-1 border-blueGray-900">
      <Gallery :photoPulls="this.idol_photos_called ? this.idol_photos_called : 244960" />
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

var axios = require('axios');

var config = {
  method: 'get',
  url: 'https://api.irenebot.com/idolcommandsused/'
};

export default {
  components: { LandingHeader, Gallery, Section, Commands },
  name: "Home",
  methods: {
    getIdolPhotosCalled(){
    /*
    Set the amount of idol photos called to live data.
    */
      return axios(config)
        .then(response => {
          this.idol_photos_called = response.data.idol_commands_used;
          }
        )
        .catch(function (error) {
          console.log(error);
        });

    }
  },
  data() {
    return {
      idol_photos_called: 0
    }
  },
  created() {
    this.getIdolPhotosCalled();
  }
};
</script>
