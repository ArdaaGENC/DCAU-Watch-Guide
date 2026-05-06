# DCAU İzleme Rehberi - Versiyon 2.2 (Süper Hata Toleranslı)

print("--- DCAU Rehberine Hoş Geldin! ---")

# Kullanıcıdan girdiyi alıyoruz.
ham_cevap = input("DCAU evreninde en son hangi seriyi bitirdin? (Lütfen tam adını yaz): ")

# Önce küçük harfe çeviriyoruz, sonra kelimelere bölüyoruz, sonra tek boşlukla birleştiriyoruz.
son_izlenen = " ".join(ham_cevap.lower().split())

# Kontrollerimiz (tamamen küçük harf ve tek boşluklu)
if son_izlenen == "batman: the animated series":
    print("Harika bir klasik! Sıradaki hedefin: The New Batman Adventures")

elif son_izlenen == "the new batman adventures":
    print("Güzel ilerliyorsun! O zaman sıradaki hedefin: Batman Beyond")

else:
    print("Hmmm, listemde bu isme göre bir yönlendirme yok. Acaba ismini mi yanlış yazdın?")