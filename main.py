# DCAU İzleme Rehberi - Versiyon 2.1 (Hata Toleranslı)

print("--- DCAU Rehberine Hoş Geldin! ---")

# input() ile ekrana bir soru yazdırıp, cevabı 'son_izlenen' değişkenine kaydediyoruz.
ham_cevap = input("DCAU evreninde en son hangi seriyi bitirdin? (Lütfen tam adını yaz): ")

# Gelen cevabı tamamen küçük harfe çevirip etrafındaki boşlukları siliyoruz.
son_izlenen = ham_cevap.lower().strip()

# Kullanıcının girdiği cevaba göre if/else mantığıyla karar veriyoruz.
if son_izlenen == "batman: the animated series":
    print("Harika bir klasik! Sıradaki hedefin: The New Batman Adventures")

elif son_izlenen == "the new batman adventures":
    print("Güzel ilerliyorsun! O zaman sıradaki hedefin: Batman Beyond")

else:
    print("Hmmm, listemde bu isme göre bir yönlendirme yok. Acaba ismini mi yanlış yazdın?")