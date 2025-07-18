<style>
.puzzle-grid {
  display: grid;
  grid-template-columns: repeat(15, 1fr);
  aspect-ratio: 1 / 1; /* 🔥 Forces it to be square */
  max-width: 9in;
  margin: 2rem auto;
  font-family: monospace;
  font-size: 1.3rem;
  line-height: 2rem;
  text-align: center;
  padding: 1rem;
  border: 2px solid #444;
  box-sizing: border-box;
}

.puzzle-wrapper {
  width: 8in;               /* Control print width */
  height: 8in;              /* Match height for square shape */
  margin: 1in auto;         /* Centered with print-safe margins */
  border: 2px solid #444;
  box-sizing: border-box;
  padding: 0.5in;
  display: grid;
  grid-template-columns: repeat(15, 1fr);
  grid-template-rows: repeat(15, 1fr);
  font-family: monospace;
  font-size: 1.3rem;
  line-height: 1;
  text-align: center;
}

.puzzle-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>


# Find the Hidden Math Problems!

There are **at least 50 math problems** hiding in the number grid below.  

Each problem uses **3 numbers** in a line written left to right, top to bottom, or diagonally moving up and to the right.  Put a **+**, **−**, **×**, or **÷** between the first two numbers, and an **=** before the last number to create a true math equation. For example, the numbers `3 5 15` could make `3 x 5 = 15`.


**How many can you find? Circle them!**


<div class="puzzle-grid">
  <div class="puzzle-cell">7</div><div class="puzzle-cell">10</div><div class="puzzle-cell">37</div><div class="puzzle-cell">17</div><div class="puzzle-cell">9</div><div class="puzzle-cell">10</div><div class="puzzle-cell">19</div><div class="puzzle-cell">4</div><div class="puzzle-cell">7</div><div class="puzzle-cell">6</div><div class="puzzle-cell">8</div><div class="puzzle-cell">19</div><div class="puzzle-cell">27</div><div class="puzzle-cell">4</div><div class="puzzle-cell">3</div>
  <div class="puzzle-cell">12</div><div class="puzzle-cell">7</div><div class="puzzle-cell">18</div><div class="puzzle-cell">6</div><div class="puzzle-cell">23</div><div class="puzzle-cell">15</div><div class="puzzle-cell">8</div><div class="puzzle-cell">8</div><div class="puzzle-cell">9</div><div class="puzzle-cell">26</div><div class="puzzle-cell">2</div><div class="puzzle-cell">13</div><div class="puzzle-cell">22</div><div class="puzzle-cell">9</div><div class="puzzle-cell">3</div>
  <div class="puzzle-cell">3</div><div class="puzzle-cell">17</div><div class="puzzle-cell">19</div><div class="puzzle-cell">23</div><div class="puzzle-cell">144</div><div class="puzzle-cell">9</div><div class="puzzle-cell">56</div><div class="puzzle-cell">15</div><div class="puzzle-cell">18</div><div class="puzzle-cell">17</div><div class="puzzle-cell">19</div><div class="puzzle-cell">323</div><div class="puzzle-cell">8</div><div class="puzzle-cell">19</div><div class="puzzle-cell">16</div>
  <div class="puzzle-cell">9</div><div class="puzzle-cell">6</div><div class="puzzle-cell">5</div><div class="puzzle-cell">12</div><div class="puzzle-cell">9</div><div class="puzzle-cell">3</div><div class="puzzle-cell">12</div><div class="puzzle-cell">6</div><div class="puzzle-cell">1</div><div class="puzzle-cell">4</div><div class="puzzle-cell">252</div><div class="puzzle-cell">8</div><div class="puzzle-cell">14</div><div class="puzzle-cell">3</div><div class="puzzle-cell">48</div>
  <div class="puzzle-cell">19</div><div class="puzzle-cell">3</div><div class="puzzle-cell">12</div><div class="puzzle-cell">13</div><div class="puzzle-cell">187</div><div class="puzzle-cell">11</div><div class="puzzle-cell">16</div><div class="puzzle-cell">17</div><div class="puzzle-cell">18</div><div class="puzzle-cell">14</div><div class="puzzle-cell">15</div><div class="puzzle-cell">18</div><div class="puzzle-cell">19</div><div class="puzzle-cell">57</div><div class="puzzle-cell">3</div>
  <div class="puzzle-cell">11</div><div class="puzzle-cell">2</div><div class="puzzle-cell">19</div><div class="puzzle-cell">8</div><div class="puzzle-cell">17</div><div class="puzzle-cell">12</div><div class="puzzle-cell">182</div><div class="puzzle-cell">17</div><div class="puzzle-cell">18</div><div class="puzzle-cell">15</div><div class="puzzle-cell">13</div><div class="puzzle-cell">144</div><div class="puzzle-cell">29</div><div class="puzzle-cell">18</div><div class="puzzle-cell">2</div>
  <div class="puzzle-cell">8</div><div class="puzzle-cell">112</div><div class="puzzle-cell">19</div><div class="puzzle-cell">35</div><div class="puzzle-cell">11</div><div class="puzzle-cell">23</div><div class="puzzle-cell">14</div><div class="puzzle-cell">34</div><div class="puzzle-cell">8</div><div class="puzzle-cell">16</div><div class="puzzle-cell">28</div><div class="puzzle-cell">19</div><div class="puzzle-cell">18</div><div class="puzzle-cell">6</div><div class="puzzle-cell">165</div>
  <div class="puzzle-cell">11</div><div class="puzzle-cell">7</div><div class="puzzle-cell">361</div><div class="puzzle-cell">18</div><div class="puzzle-cell">7</div><div class="puzzle-cell">10</div><div class="puzzle-cell">13</div><div class="puzzle-cell">8</div><div class="puzzle-cell">17</div><div class="puzzle-cell">10</div><div class="puzzle-cell">27</div><div class="puzzle-cell">3</div><div class="puzzle-cell">11</div><div class="puzzle-cell">3</div><div class="puzzle-cell">11</div>
  <div class="puzzle-cell">10</div><div class="puzzle-cell">16</div><div class="puzzle-cell">15</div><div class="puzzle-cell">13</div><div class="puzzle-cell">132</div><div class="puzzle-cell">5</div><div class="puzzle-cell">64</div><div class="puzzle-cell">17</div><div class="puzzle-cell">1</div><div class="puzzle-cell">15</div><div class="puzzle-cell">37</div><div class="puzzle-cell">19</div><div class="puzzle-cell">18</div><div class="puzzle-cell">3</div><div class="puzzle-cell">15</div>
  <div class="puzzle-cell">5</div><div class="puzzle-cell">270</div><div class="puzzle-cell">7</div><div class="puzzle-cell">28</div><div class="puzzle-cell">12</div><div class="puzzle-cell">32</div><div class="puzzle-cell">8</div><div class="puzzle-cell">4</div><div class="puzzle-cell">5</div><div class="puzzle-cell">18</div><div class="puzzle-cell">8</div><div class="puzzle-cell">12</div><div class="puzzle-cell">20</div><div class="puzzle-cell">8</div><div class="puzzle-cell">3</div>
  <div class="puzzle-cell">2</div><div class="puzzle-cell">20</div><div class="puzzle-cell">16</div><div class="puzzle-cell">24</div><div class="puzzle-cell">11</div><div class="puzzle-cell">17</div><div class="puzzle-cell">7</div><div class="puzzle-cell">19</div><div class="puzzle-cell">13</div><div class="puzzle-cell">32</div><div class="puzzle-cell">19</div><div class="puzzle-cell">4</div><div class="puzzle-cell">21</div><div class="puzzle-cell">24</div><div class="puzzle-cell">2</div>
  <div class="puzzle-cell">17</div><div class="puzzle-cell">12</div><div class="puzzle-cell">288</div><div class="puzzle-cell">21</div><div class="puzzle-cell">19</div><div class="puzzle-cell">13</div><div class="puzzle-cell">12</div><div class="puzzle-cell">1</div><div class="puzzle-cell">210</div><div class="puzzle-cell">15</div><div class="puzzle-cell">14</div><div class="puzzle-cell">210</div><div class="puzzle-cell">3</div><div class="puzzle-cell">13</div><div class="puzzle-cell">1</div>
  <div class="puzzle-cell">9</div><div class="puzzle-cell">7</div><div class="puzzle-cell">5</div><div class="puzzle-cell">16</div><div class="puzzle-cell">4</div><div class="puzzle-cell">5</div><div class="puzzle-cell">5</div><div class="puzzle-cell">4</div><div class="puzzle-cell">7</div><div class="puzzle-cell">3</div><div class="puzzle-cell">90</div><div class="puzzle-cell">14</div><div class="puzzle-cell">51</div><div class="puzzle-cell">19</div><div class="puzzle-cell">8</div>
  <div class="puzzle-cell">8</div><div class="puzzle-cell">10</div><div class="puzzle-cell">9</div><div class="puzzle-cell">1</div><div class="puzzle-cell">18</div><div class="puzzle-cell">17</div><div class="puzzle-cell">5</div><div class="puzzle-cell">8</div><div class="puzzle-cell">16</div><div class="puzzle-cell">1</div><div class="puzzle-cell">9</div><div class="puzzle-cell">15</div><div class="puzzle-cell">3</div><div class="puzzle-cell">3</div><div class="puzzle-cell">19</div>
  <div class="puzzle-cell">4</div><div class="puzzle-cell">3</div><div class="puzzle-cell">2</div><div class="puzzle-cell">14</div><div class="puzzle-cell">28</div><div class="puzzle-cell">1</div><div class="puzzle-cell">7</div><div class="puzzle-cell">3</div><div class="puzzle-cell">21</div><div class="puzzle-cell">4</div><div class="puzzle-cell">10</div><div class="puzzle-cell">2</div><div class="puzzle-cell">17</div><div class="puzzle-cell">16</div><div class="puzzle-cell">2</div>
</div>

**Challenge:** Can you find other math equations that use more than three numbers or have different shapes than straight lines.