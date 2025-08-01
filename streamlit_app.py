import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# CSV dosyasını oku (veri dosya yolunu kendi konumuna göre ayarla)
df = pd.read_csv("premier_league_2024_25.csv")

st.title("Premier League Gol Krallığı Analizi – 2024/25")


# Oyuncu seçimi için dropdown
player = st.selectbox("Bir oyuncu seç:", df['Player'])

# Seçilen oyuncunun verisi
selected = df[df['Player'] == player].squeeze()

st.subheader(f"{player} – Performans Özeti")

# Seçilen oyuncunun ek bilgileri
st.markdown(f"""
- 🌍 Ülke: `{selected['Nation']}`
- 🏢 Takım: `{selected['Squad']}`
- 🏟️ Maç Sayısı: `{selected['MP']}`
- ⏱️ Oynadığı Dakika: `{selected['Minutes']}`
- ⚽ Goller: `{selected['Goals']}`
""")

st.markdown(f"""
- 🎯 Goller / 90 dk: `{selected['Per 90 Minutes_Gls']:.2f}`
- 📈 xG / 90 dk: `{selected['Per 90 Minutes_xG']:.2f}`
- 🅰️ Asistler / 90 dk: `{selected['Per 90 Minutes_Ast']:.2f}`
- ⚙️ xAG / 90 dk: `{selected['Per 90 Minutes_xAG']:.2f}`
""")


def generate_ai_comment(player_data):
    goals = player_data['Per 90 Minutes_Gls']
    xg = player_data['Per 90 Minutes_xG']
    ast = player_data['Per 90 Minutes_Ast']
    xag = player_data['Per 90 Minutes_xAG']

    comments = []
    if goals > xg + 0.2:
        comments.append("Oyuncu gol sayısını beklentisinin üzerinde tutuyor, iyi bir bitirici.")
    elif goals < xg - 0.2:
        comments.append("Oyuncunun gol sayısı beklentinin altında, daha iyi değerlendirebilir.")
    else:
        comments.append("Gol sayısı beklentilerle uyumlu.")

    if ast > 0.3:
        comments.append("Asist katkısı yüksek, oyun kurma yeteneği güçlü.")
    else:
        comments.append("Asist sayısı düşük, pasör rolü sınırlı olabilir.")

    return " ".join(comments)


ai_comment = generate_ai_comment(selected)
st.markdown("### Kısa Yorum")
st.info(ai_comment)


# Seçilen oyuncu için bar grafiği
fig, ax = plt.subplots()
metrics = {
    "Goller": selected['Per 90 Minutes_Gls'],
    "xG": selected['Per 90 Minutes_xG'],
    "Asist": selected['Per 90 Minutes_Ast'],
    "xAG": selected['Per 90 Minutes_xAG']
}
ax.bar(metrics.keys(), metrics.values(), color=['darkgreen', 'gray', 'royalblue', 'lightgray'])
ax.set_title("Seçilen Oyuncunun Ofansif Metrikleri")
st.pyplot(fig)


# 2) Scatter Plot - xG vs Golleri karşılaştır
st.subheader("xG vs Gerçek Gol Dağılımı")
fig_scatter, ax_scatter = plt.subplots(figsize=(8,6))
sns.scatterplot(data=df, x="Per 90 Minutes_xG", y="Per 90 Minutes_Gls", hue="Player", palette='tab10', ax=ax_scatter)
ax_scatter.plot([0, max(df["Per 90 Minutes_xG"])], [0, max(df["Per 90 Minutes_xG"])], "r--")
# Seçilen oyuncunun noktasını vurgula
ax_scatter.scatter(selected['Per 90 Minutes_xG'], selected['Per 90 Minutes_Gls'], color='red', s=150, edgecolor='black', label=player)
ax_scatter.legend()
st.pyplot(fig_scatter)

# 3) Boxplot - Pozisyona göre gol dağılımı
st.subheader("Pozisyona Göre Gol / 90 Dakika Dağılımı")
fig_box, ax_box = plt.subplots(figsize=(8,6))
sns.boxplot(data=df, x="Position", y="Per 90 Minutes_Gls", ax=ax_box)

import plotly.graph_objects as go

# Performans metriklerini seç
categories = ['Per 90 Minutes_Gls', 'Per 90 Minutes_xG', 'Per 90 Minutes_Ast', 'Per 90 Minutes_xAG']

values = [selected[cat] for cat in categories]
values += values[:1]  # radar kapalı döngü için ilk değer tekrar

fig = go.Figure(
    data=[
        go.Scatterpolar(r=values, theta=categories + [categories[0]], fill='toself', name=player)
    ],
    layout=go.Layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(values)*1.2])),
        showlegend=False,
        title=f"{player} - Performans Profili (Radar Grafik)"
    )
)
st.plotly_chart(fig)



# Çoklu oyuncu seçimi
players_selected = st.multiselect("Bir veya birden fazla oyuncu seç:", df['Player'].unique(), default=[df['Player'].iloc[0]])

if players_selected:
    st.subheader("Seçilen Oyuncuların Karşılaştırması")

    # Performans metrikleri
    categories = ['Per 90 Minutes_Gls', 'Per 90 Minutes_xG', 'Per 90 Minutes_Ast', 'Per 90 Minutes_xAG']

    # Yeni bir DataFrame oluştur seçilen oyuncuların verileriyle
    compare_df = df[df['Player'].isin(players_selected)][['Player'] + categories].set_index('Player')

    # Bar plot karşılaştırması (matplotlib ile)
    fig, ax = plt.subplots(figsize=(10, 6))
    compare_df.T.plot(kind='bar', ax=ax)
    ax.set_ylabel("Değer")
    ax.set_title("Oyuncu Performans Metrikleri Karşılaştırması (Per 90 Dakika)")
    st.pyplot(fig)

    # Çoklu oyuncu için radar grafiği
    fig_radar = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    for i, player in enumerate(players_selected):
        player_values = compare_df.loc[player].tolist()
        player_values += player_values[:1]  # radar kapalı döngü için ilk değer tekrar
        fig_radar.add_trace(go.Scatterpolar(r=player_values, theta=categories + [categories[0]], fill='toself', name=player, line=dict(color=colors[i % len(colors)])))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, compare_df.max().max()*1.2])),
        showlegend=True,
        title="Seçilen Oyuncular - Performans Profili (Radar Grafik)"
    )
    st.plotly_chart(fig_radar)
    st.markdown("Bu radar grafiği, seçilen oyuncuların farklı performans metriklerindeki başarılarını karşılaştırır. Her bir oyuncu farklı bir renkle temsil edilmiştir.")

    # Çoklu oyuncu için ısı haritası
    st.subheader("Seçilen Oyuncular İçin Performans Metrikleri Isı Haritası")
    fig_heatmap, ax_heatmap = plt.subplots(figsize=(10, 6))
    sns.heatmap(compare_df, annot=True, fmt=".2f", cmap="YlGnBu", ax=ax_heatmap)
    ax_heatmap.set_title("Seçilen Oyuncular - Performans Metrikleri Isı Haritası")
    st.pyplot(fig_heatmap)
    st.markdown("Bu ısı haritası, seçilen oyuncuların performans metriklerini renk yoğunluğu ile gösterir. Daha koyu renkler daha yüksek performansı temsil eder.")

    # Çoklu oyuncu için xG vs Gerçek Gol Dağılımı
    st.subheader("Seçilen Oyuncular için xG vs Gerçek Gol Dağılımı")
    fig_scatter_multi, ax_scatter_multi = plt.subplots(figsize=(8,6))
    for player in players_selected:
        player_data = df[df['Player'] == player]
        ax_scatter_multi.scatter(player_data['Per 90 Minutes_xG'], player_data['Per 90 Minutes_Gls'], label=player, s=100)
    ax_scatter_multi.plot([0, max(df['Per 90 Minutes_xG'])], [0, max(df['Per 90 Minutes_xG'])], "r--")
    ax_scatter_multi.set_xlabel("xG")
    ax_scatter_multi.set_ylabel("Gerçek Goller")
    ax_scatter_multi.legend()
    st.pyplot(fig_scatter_multi)
    st.markdown("Bu dağılım grafiği, seçilen oyuncuların beklenen goller (xG) ile gerçek gollerini karşılaştırır. Kırmızı kesikli çizgi, xG ve gerçek goller arasında ideal bir eşleşmeyi temsil eder.")

    # Karşılaştırma için ek grafikler
    st.subheader("Seçilen Oyuncuların Maç Sayısı Ve Goller Karşılaştırması")
    compare_categories = ['MP', 'Goals']
    compare_df_extended = df[df['Player'].isin(players_selected)][['Player'] + compare_categories].set_index('Player')

    # Bar plot karşılaştırması (matplotlib ile)
    fig_compare, ax_compare = plt.subplots(figsize=(10, 6))
    compare_df_extended.T.plot(kind='bar', ax=ax_compare)
    ax_compare.set_ylabel("Değer")
    ax_compare.set_title("Oyuncu Performans Metrikleri Karşılaştırması (Maç Sayısı, Goller)")
    st.pyplot(fig_compare)


import io

# Seçilen oyuncuların verilerini CSV olarak indir
if players_selected:
    csv = df[df['Player'].isin(players_selected)].to_csv(index=False)
    st.download_button(
        label="Seçilen Oyuncuların Verisini CSV olarak indir",
        data=csv,
        file_name='players_selected_data.csv',
        mime='text/csv'
    )


