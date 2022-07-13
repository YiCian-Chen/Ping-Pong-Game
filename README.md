# Ping-Pong-Game
2D Ping-Pong game supports double player mode(using socket)
此專案為學習socket使用，搭配小遊戲實作

## PIP 安裝 requirements.txt 的套件
在此檔案目錄下輸入以下指令，即可安裝套件

pip install -r requirements.txt

## 遊戲介紹
1.有3種模式(AI vs AI, Player vs Ai, Player vs Player)
2.使用上下方向鍵來移動
3.玩家可以按 Esc 鍵離開遊戲
4.單人模式中，玩家在左邊，AI在右邊
5.雙人模式中，Server端在左邊，Client端在右邊，雙方都必須輸入Server端的IP

## 程式簡介
* 有單人模式可以用來打發時間，也可以和朋友雙人連線遊玩
* 雙人模式中，期中一邊當server，另一邊當client，雙方都需輸入server方的IP
* 建議有固定IP可以直接連線，或是在區網內遊玩

* 遊戲選單
![](https://i.imgur.com/7eqs5FR.png)

* 雙人模式選單
![](https://i.imgur.com/SCWk8cE.png)

* 規則介紹
![](https://i.imgur.com/Zz6j9DV.png)

* 遊戲畫面
![](https://i.imgur.com/O5nghiy.png)


## 未來可更新項目
* 球反彈牆壁或球拍時，加入音效
* 加入遊戲背景音樂
* 將球的樣式改成圖片
* AI擊球演算法的調整，加入計算牆壁反彈後的目標點
* 更新模式:球可隨時間來加速
* 更新模式:加入道具系統:可讓自己或對手球拍變長或縮短或改變移動速度，加入多顆球等

## 參考資料
#### Socket
[IT邦幫忙:在資訊宅中打滾的通訊系生-Day-12 Python_Socket小實作](https://ithelp.ithome.com.tw/articles/10205819)

[GITHUB:InvincibleAoXiang/python-socket-TicTacToe](https://github.com/InvincibleAoXiang/python-socket-TicTacToe)

#### pygame
[YT:GrandmaCan我阿嬤都會-pygame 3小時製作一個遊戲](https://www.youtube.com/watch?v=61eX0bFAsYs)
