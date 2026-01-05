const templateBtn = document.getElementById("templateBtn");
const generateBtn = document.getElementById("generateBtn");
const facultySelect = document.getElementById("faculty");
const themeInput = document.getElementById("theme");
const lengthSelect = document.getElementById("length");
const regMsg = document.getElementById("regMsg")

templateBtn.addEventListener("click", () => {
  const humanities = {
      theme:"SNSの普及が現代の若者の価値観と人間関係に与えた変化について具体例を交えて考察しなさい。",
      faculty:"humanities",
      length:"1000"
    }

  const science = {
      theme:"再生可能エネルギーの導入拡大における技術的課題と解決の方向性について、発電効率・コスト・環境負荷の観点から考察しなさい。",
      faculty:"science",
      length:"2000"
    }

  const mixed = {
      theme:"インターネットの発展が、現代の生活・社会・科学技術に与えた影響を整理し、その利点と課題について述べなさい。",
      faculty:"mixed",
      length:"500"
    }

  const templates = [humanities,science,mixed]
  const rand = Math.floor(Math.random()*3);
  const t = templates[rand]
  themeInput.value = t.theme;
  facultySelect.value = t.faculty;
  lengthSelect.value = t.length;
});

generateBtn.addEventListener("click", async () => {
  const theme = themeInput.value.trim();
  const faculty = facultySelect.value;
  const length = Number(lengthSelect.value);

  // 入力チェック（最低限）
  if (!faculty || !theme || !length) {
    alert("学部系・課題文・文字数をすべて入力してください");
    return;
  }

  document.getElementById("plan1").innerText = "生成中...";
  document.getElementById("plan2").innerText = "生成中...";
  document.getElementById("plan3").innerText = "生成中...";

  try {
    // ローカルでもRenderでも同じ：同一ドメインにPOSTする
    const response = await fetch("/structure", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: theme, faculty, length })
    });

    if (!response.ok) {
      const txt = await response.text();
      throw new Error("HTTP " + response.status + " / " + txt);
    }

    const data = await response.json();

    document.getElementById("plan1").innerText = data.plan1 ?? "生成失敗";
    document.getElementById("plan2").innerText = data.plan2 ?? "生成失敗";
    document.getElementById("plan3").innerText = data.plan3 ?? "生成失敗";

  } catch (e) {
    document.getElementById("plan1").innerText = "エラー: " + e;
    document.getElementById("plan2").innerText = "エラー";
    document.getElementById("plan3").innerText = "エラー";
  }
});

const questionBtn = document.getElementById("questionBtn");
questionBtn.addEventListener("click", () => {
  let reg_text = "仮登録しました！メール入力で本登録・特典GET";
  const msgPlace = document.getElementById("regMsg");
  msgPlace.innerText = reg_text;
  form.style.display = "block";
  
  fetch("/api/clicklog",{
    method: "POST"
  })
  fetch.then(res => res.json()).then(j => console.log(j.clicks))
});

const regName = document.getElementById("regName");
const regEmail = document.getElementById("regEmail");
const regForm = document.getElementById("regForm")
regForm.addEventListener("submit",(e) => {
  e.preventDefault()
  const user_data = {
    name: regName.value, 
    email: regEmail.value
  }
  fetch("/api/preregister",{
    method: "POST",
    body : JSON.stringify(user_data)
  })
  .then(() => alert("登録できた！"))
})