<template>
  <div id="app">

    <v-app>
      <main>
        <v-container>
          <v-layout row wrap>
           <v-flex xs3>
           <v-select
              label="Country"
              v-bind:items="locations"
              v-model="gl"
              item-text="name"
              item-value="iso"
              multiple
              chips
              dark
              autocomplete
              @input="fetchResults('gl')"
            >
              <template slot="selection" scope="data">
                <v-chip
                  @input="data.parent.selectItem(data.item)"
                  @click.native.stop
                  class="chip--select-multi"
                  :key="data.item"
                  close
                >
                  <v-avatar>
                    <flag :iso="data.item.iso" class="flag"/>
                  </v-avatar>
                  {{ data.item.name }}
                </v-chip>
              </template>
              <template slot="item" scope="data">
                <v-list-tile-avatar>
                  <flag v-bind:iso="data.item.iso" class="flag"/>
                </v-list-tile-avatar>
                <v-list-tile-content>
                  <v-list-tile-title v-html="data.item.name"></v-list-tile-title>
                </v-list-tile-content>
              </template>
            </v-select>  

          </v-flex>
          <v-flex xs3>
          <!-- <span v-for="engine in searchengines">
            <v-checkbox :label="engine.api" v-model="apis" :value="engine.api" ></v-checkbox>
          </span> -->
          <v-checkbox label="Google" v-model="apis" value="google"></v-checkbox>
          <v-checkbox label="Baidu" v-model="apis" value="baidu"></v-checkbox>
          <v-checkbox label="Bing" v-model="apis" value="bing"></v-checkbox>

          </v-flex>
           <v-flex xs3>
             <v-text-field 
             name="search term"
             label="search"
             id="search"
             v-model="input"
             @input="fetchResults('query')"
             ></v-text-field>
           </v-flex>
           <v-flex xs3>
             <v-text-field 
             name="extra term"
             label="parameters"
             id="params"
             v-model="params"
             @input="fetchResults('query')"
             ></v-text-field>
           </v-flex>
         </v-layout>
         <v-layout row>
           <v-flex l4>
             <!-- <v-card class="blue darken-1 white--text mt-3"> -->
               <!-- <v-card-text> -->
                 <div class="" v-if="output">
                 <div v-for="(result, i) in output" :style="[{float: (i % 2 == 0) ? 'left':'right'}, {'width': '25%'}]">
                    <!-- <v-chip close><flag :iso="obj.gl" class="flag"/>{{obj.result}}</v-chip> -->
                    <!-- <v-chip close>{{result.result}}</v-chip> -->
                      <div v-for="(words, j) in result.result" :style="[{float: (i % 2 == 0) ? 'left':'right'}, 'display: inline;', 'width: 40%']" :class="result.api">
                        <v-chip :key="j">
                          <v-avatar>
                            <flag :iso="result.country" class="flag"/>
                          </v-avatar>
                          {{ words }}
                        </v-chip>
                      </div>
                    
                  </div>
                </div>
                <div v-if="error">
                  {{error}}
                </div>
               <!-- </v-card-text> -->
             <!-- </v-card> -->
           </v-flex>
         </v-layout>


       </v-container>
     </main>
     <v-footer class="grey py-4">
      <p>2017 Edan Weis</p>
    </v-footer>
  </v-app>

</div>
</template>

<script>
  var Q = require('q');
  import _ from 'lodash'
  var countries = require('./assets/countries.json')
  // import axios from 'axios'
  import jsonpP from 'jsonp-p'
  export default {
    data: function() {
      return {
        input: '',
        params: '',
        output: [
          ]
          ,
        locations: countries,
        error: null, 
        gl: [],
        apis: [],
        searchengines: {
          google: {
            root: "https://clients1.google.com/complete/search?client=chrome&hl=en",
            callback: "jsonp",
            gl: "&gl=",
            api: "Google"
          },
          baidu:{
            root: "http://suggestion.baidu.com/su?wd=",
            callback: "cb",
            gl: "&gl=",
            api: "Baidu"
        },
          bing: {
            root: "http://api.bing.com/qsonhs.aspx?type=cb&q=",
            callback: "cb",
            gl: "&gl=",
            api: "Bing"
          }   
      }
    }
    },
    name: 'app',
    components: {
    }, 
    created: function () {
      window.addEventListener('keyup', function(event){
        var key = event.key
        if(event.key =="ArrowUp"){
          // self.gl="il"
        }
        
      })
    },
    computed: {

    },
    methods: {
      
      getJSON: function(url, callback){
        return jsonpP(url, {param: (callback||'')}).promise
      },
      
      changeLocation(e){
        this.gl = e
        self.output = []
        this.fetchResults()
      },
      
      callAPIs: function(input, gl, apis){
        // console.log(this.)

        var self = this
        var data = []
        var promises = []
        var index = []
        for (var i = gl.length - 1; i >= 0; i--) {
          for (var z = apis.length - 1; z >= 0; z--) {
            // console.log(self.searchengines, apis[z])
            let api = self.searchengines[apis[z]]
            // console.log(api)
            promises.push(this.getJSON( String(api.root + "&" + self.params + api.gl.toLowerCase() + gl[i] + "&q="+input ), api.callback ))
            index.push({"api": api.api, "gl":gl[i], "index": {"gl": i, "api": z}})
          }
        }
        return Q.allSettled(promises.map(function(result, i) {
          return result.then(res =>{
            if (index[i].api == "Google"){
              return {"result": res[1], "country": index[i].gl, "api": "Google" }
            } else if(index[i].api == "Baidu"){
              return {"result": res['s'], "country": index[i].gl, "api": "Baidu" }
            } else if(index[i].api == "Bing"){
              return {"result": _.map(_.map(res['AS'].Results, 'Suggests'), 'Txt'), "country": index[i].gl, "api": "Bing" }
            }
          })
        }))
        .then(result =>{
          self.output = _.map(result, 'value')
          
          // self.output = result
        })

      },
      
      fetchResults:  _.debounce(function (action){
        // console.log('fetching results')  
        if(this.input && this.gl ){
          this.callAPIs(this.input, this.gl, this.apis)
        } else{
          // console.log('input or gl not specified')
        }
      }, 50)

    }
  }
</script>

<style lang="stylus">
  @import './stylus/main'

  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
  }
  
  .flag{
    // width: 100px;
    // height: 100px;
    font-size: 2em;
    border-radius: 50%;
  }
  .avatar{
    justify-content: center !important;
  }
  
  .Baidu .chip{
    background: #FC5442 !important;
    color: white;
  }
  .Google .chip{
    background: #89E9FA !important;  
  }
  
  .Bing .chip{
    background: #F3FA89 !important;  
  }
</style>
