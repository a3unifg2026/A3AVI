```css
body{
    margin: 0;
    padding: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #dfe6ee;
}
/* TOPO */
.topo{
    width: 100%;
    background: #1d3557;
    padding: 18px;
    color: white;
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.topo h1{
    margin: 0;
    color: white;
}
/* CONTAINER */
.container{
    width: 92%;
    max-width: 1250px;
    margin: auto;
    margin-top: 25px;
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 0 15px rgba(0,0,0,0.08);
    box-sizing: border-box;
}
/* TITULOS */
h2,h3{
    color: #1d3557;
}
/* MENU */
.menu{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 20px;
}
/* BOTÕES */
button{
    background: #1d3557;
    color: white;
    border: none;
    padding: 11px 18px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    transition: 0.2s;
}
button:hover{
    background: #274c77;
    transform: scale(1.03);
}
/* INPUTS */
input,
textarea{
    width: 100%;
    padding: 12px;
    border-radius: 6px;
    border: 1px solid #c7c7c7;
    margin-top: 5px;
    margin-bottom: 15px;
    box-sizing: border-box;
    font-size: 15px;
}
/* TABELAS */
table{
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    overflow: hidden;
    border-radius: 8px;
}
table th{
    background: #1d3557;
    color: white;
    padding: 14px;
    font-size: 15px;
}
table td{
    padding: 13px;
    border-bottom: 1px solid #e1e1e1;
    text-align: center;
    font-size: 14px;
}
table tr:nth-child(even){
    background: #f7f9fc;
}
table tr:hover{
    background: #edf3ff;
}
/* LINKS */
a{
    text-decoration: none;
    color: #1d3557;
    font-weight: bold;
}
a:hover{
    color: #457b9d;
}
/* FUNCIONÁRIO DESLIGADO */
.desligado{
    background: #ffdede !important;
}
/* AVISOS */
.card{
    background: #f5f7fa;
    border-left: 5px solid #1d3557;
    padding: 18px;
    margin-bottom: 18px;
    border-radius: 6px;
}
/* DARK MODE */
.dark{
    background: #121212;
}
.dark .container{
    background: #1f1f1f;
}
.dark table tr:nth-child(even){
    background: #232323;
}
.dark table td{
    color: white;
    border-color: #333;
}
.dark h2,
.dark h3{
    color: white;
}
.dark input,
.dark textarea{
    background: #2b2b2b;
    color: white;
    border: 1px solid #444;
}
.dark .card{
    background: #2a2a2a;
    color: white;
}
```