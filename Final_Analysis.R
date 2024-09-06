#Jonathan Ko
#CS544
#Final Project
#Spotify Top Hits 2000-2019
help("ggPairs")
library(tidyverse)
file <- read.csv("/Users/jonathanko/Documents/School/CS544/Final_Project/songs_normalize.csv")
SpotifyTopHits <- as_tibble(file)
help("plot_ly")



#Group by pop songs only
Spotify_TopHits_Pop <- str_subset(SpotifyTopHits$genre, "pop")

#Categorical Variable - Genre
barplot(table(trimws(unlist(str_split(SpotifyTopHits$genre, ",")))),
        col = "cyan", xlim = c(1, 20), ylim = c(0,1700), las = 2,
        cex.axis = 1, cex.names = par("cex.axis"),
        xlab= "Genres", ylab = "Frequencies of Song Genres")

SpotifyTopHits_genre <- trimws(unlist(str_split(SpotifyTopHits$genre, ",")))
y <- as_tibble(SpotifyTopHits_genre)
p <- plot_ly(x = SpotifyTopHits_genre, type="bar", name = 'Genres')
p


SpotifyHits2000s <- SpotifyTopHits %>%
  filter(year >= 1998 & year <= 2009)

SpotifyHits2010s <- SpotifyTopHits %>%
  filter(year > 2009 & year < 2020)

barplot(table(trimws(unlist(str_split(SpotifyTopHits$genre, ",")))),
        col = "cyan", xlim = c(1, 20), ylim = c(0,1700), las = 2,
        cex.axis = 1, cex.names = par("cex.axis"),
        xlab= "Genres", ylab = "Frequencies of Song Genres")

#Categorical Variable - Key
code <- SpotifyTopHits$key
key_notes <- c("N/A","C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb")
keys <- key_notes[code+1]
SpotifyTopHits$keys <- keys

table(SpotifyTopHits$keys)
mean(table(SpotifyTopHits$keys))
sd(table(SpotifyTopHits$keys))

#Categorical variable - Explicit FALSE TRUE
explicit <- SpotifyTopHits$explicit
SpotifyTopHits$explicitness <- as.integer(as.logical(explicit))

barplot(table(SpotifyTopHits$keys),
        col = "cyan", xlim = c(1, 20), ylim = c(0,275), las = 2,
        cex.axis = 1, cex.names = par("cex.axis"),
        xlab= "Keys", ylab = "Frequencies of Song Keys")


#Numerical Variable - Tempo
barplot(table(round(SpotifyTopHits$tempo,0)),
        col = "cyan", xlim = c(0,211), ylim = c(0,80), las = 2,
        cex.axis = 1.3, cex.names = 1.3,
        xlab= "Tempo of Songs", ylab = "Frequency of Tempo Songs")

#2Sets Year by average tempo
spotifyYearbyaveragetempoPlot <- SpotifyTopHits |>
  group_by(year) |>
  summarise(tempo = mean(tempo))
barplot(spotifyYearbyaveragetempoPlot$tempo, xlab = "Year",
        ylab = "Tempos", col = "cyan", las = 2, ylim = c(0,140),
        main = "Average Tempos"
)

#2Sets Year by average energy
spotifyYearbyaverageenergyPlot <- SpotifyTopHits |>
  group_by(year) |>
  summarise(energy = mean(energy))
barplot(spotifyYearbyaverageenergyPlot$energy, xlab = "Year",
        ylab = "Energy", col = "cyan", las = 2, ylim = c(0,1),
        main = "Average Energy Per Year"
)

#2Sets Year by Explicit
help("data.frame")
barplot(table(SpotifyTopHits$explicit,SpotifyTopHits$year), xlab = "Year",
        ylab = "Energy", col = c("cyan","burlywood"), las = 2, legend.text = c("Y", "N"),
        angle = 45,
        main = "Explicit/Not Explicit Songs across 1999-2020"
)

x_explicit <- data.frame(SpotifyTopHits$year, SpotifyTopHits$explicit)

pexplicit <- plot_ly(x_explicit, type="bar")  %>%
  layout(
    title = "Spotify Top Hits Year by Year Explicitness",
    xaxis = list(title = "Years"),
    yaxis = list(title = "Song Explicitness Count")
  )
pexplicit


#which years had the best popularity scores and worst
max_ind_Spotify_score <- which.max(SpotifyTopHits$popularity)
min_ind_Spotify_score <- which.min(SpotifyTopHits$popularity)

max_Spotify_score <- SpotifyTopHits$popularity[max_ind_Spotify_score]
min_Spotify_score <- SpotifyTopHits$popularity[min_ind_Spotify_score]
max_Spotify_score
min_Spotify_score

#Correlation matrix for the variables
install.packages("corrplot")
library(corrplot)
pairs(~ duration_ms + explicitness + year + popularity + danceability + energy +
        key + loudness + mode + speechiness + acousticness + instrumentalness + 
        liveness + valence + tempo, data = SpotifyTopHits)

SpotifyTopHitscor <- subset(SpotifyTopHits, select = -c(artist, song, explicit, genre, keys))
cm <- round(cor(SpotifyTopHitscor),2)
cm

for (i in 1:nrow(cm)) {
  attributes <- rownames(cm)[i]
  topcor <- order(cm[,i], decreasing = TRUE)[2:4]
  topcoratt <- rownames(cm)[topcor]
  topcorvalue <- cm[topcoratt,i]
  cat("Top 3 for stock", attributes, "\n")
  cat("Top Correlated Attributes", topcoratt, "\n")
  cat("Top Correlation Values",topcorvalue, "\n\n")
}

corrplot(cm, type = "upper", order = "hclust", 
         tl.col = "black", tl.srt = 45)


#Sampling Songs at Random for average length of a song
library(sampling)
par(mfrow = c(1,1))
y <-  SpotifyTopHits$duration_ms
mins_y <- y/60000
hist(mins_y, xlab = "Length", ylab = "Frequency", main = "Top Hits Duration", xaxt = "n")
axis(side = 1, at = seq(from = 0, to = 6, by = 0.1), labels = TRUE)
axis(side = 2, at = seq(from = 0, to = 2000, by = 1000),     # side=2: left
     labels = TRUE)

mean_mins_y <- mean(mins_y)
sd_mins_y <- sd(mins_y)

set.seed(3192)
samples <- 1000
sample.size <- c(10,20,30,40)
xbar <- numeric(samples)
par(mfrow = c(2,2))

for (size in sample.size) {
  for (i in 1:samples) {
    xbar[i] <- mean(sample(mins_y, size = size, replace = FALSE))
  }
  
  hist(xbar, prob = TRUE, 
       breaks = 15,
       main = paste("Sample Size =", size))
  
  cat("Sample Size = ", size, " Mean = ", mean(xbar),
      " SD = ", sd(xbar), "\n")
}

#Show the sample drawn using simple random sampling with replacement. Show the
#frequencies for the selected genres Show the percentages of these with respect
#to sample size.
#Sampling Songs at at random for genre of music
sample.size <- 50
top5_genres <- sort(table(SpotifyTopHits$genre), decreasing = TRUE)[1:5]
data <- subset(SpotifyTopHits, genre %in% names(top5_genres))
s <- srswr(sample.size, nrow(data))
s[s != 0]
rows <- (1:nrow(data))[s!=0]
rows <- rep(rows, s[s != 0])
sample.1 <- data[rows, ]
freq <- table(sample.1$genre)
st.percent <- prop.table(freq) * 100
top5_genres
freq
st.percent

#Calculate the inclusion probabilities using the duration variable. Using these values,
#show the sample drawn using systematic sampling with unequal probabilities. Show the
#frequencies for the selected genres Show the percentages of these with respect
#to sample size.

N <- nrow(data)
k <- ceiling(N/sample.size)
r <- sample(k,1)
s <- seq(r, by = k, length = sample.size)
sample.2 <- data[s, ]
freq <- table(sample.2$genre)
st.percent <- prop.table(freq) * 100
freq
st.percent

pik <- inclusionprobabilities(data$duration_ms,50)
s <- UPsystematic(pik)
sample.3 <- data[s != 0, ]
freq <- table(sample.3$genre)
st.percent <- prop.table(freq) * 100
freq
st.percent

#Order the data using the Genre variable. Draw a stratified sample using
#proportional sizes based on the Genre variable. Show the frequencies for the
#selected genres Show the percentages of these with respect to sample size.

order.index <- order(data$genre)
sample.4 <- data[order.index, ]
freq <- table(sample.4$genre)
st.percent <- prop.table(freq) * 100
freq
st.percent
st.sizes <- 50 * freq / sum(freq)

st.2 <- sampling::strata(sample.4, stratanames = c("genre"),
                         size = st.sizes, method = "srswor",
                         description = TRUE)

st.sample4 <- getdata(sample.4, st.2)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sample.size <- 50
top5_genres
top5_genres <- sort(table(SpotifyTopHits$genre), decreasing = TRUE)[1:5]
data <- subset(SpotifyTopHits, genre %in% names(top5_genres))

s <- srswr(sample.size, nrow(data))
rows <- (1:nrow(data))[s!=0]
rows <- rep(rows, s[s != 0])
sample.1 <- data[rows, ]
freq.1 <- table(sample.1$genre)
st.percent.1 <- prop.table(freq.1) * 100

#Calculate the inclusion probabilities using the duration variable. Using these values,
#show the sample drawn using systematic sampling with unequal probabilities. Show the
#frequencies for the selected genres Show the percentages of these with respect
#to sample size.

N <- nrow(data)
k <- ceiling(N/sample.size)
r <- sample(k,1)
s <- seq(r, by = k, length = sample.size)
sample.2 <- data[s, ]
freq.2 <- table(sample.2$genre)
st.percent.2 <- prop.table(freq.2) * 100


pik <- inclusionprobabilities(data$duration_ms,50)
s <- UPsystematic(pik)
sample.3 <- data[s != 0, ]
freq.3 <- table(sample.3$genre)
st.percent.3 <- prop.table(freq.3) * 100


#Order the data using the Genre variable. Draw a stratified sample using
#proportional sizes based on the Genre variable. Show the frequencies for the
#selected genres Show the percentages of these with respect to sample size.

order.index <- order(data$genre)
sample.4 <- data[order.index, ]
freq.4 <- table(sample.4$genre)
st.percent.4 <- prop.table(freq.4) * 100

st.sizes <- 50 * freq.4 / sum(freq.4)

st.2 <- sampling::strata(sample.4, stratanames = c("genre"),
                         size = st.sizes, method = "srswor",
                         description = TRUE)

st.sample4 <- getdata(sample.4, st.2)

sample.1$genre
sample.2$genre
sample.3$genre
sample.4$genre

par(mfrow = c(2,2))

for (size in c(10, 20, 30, 40)) {
  for (i in 1:samples) {
    xbar[i] <- mean(sample(x, size = size, 
                           replace = TRUE))
    
  }
  
  hist(xbar, prob = TRUE, 
       breaks = 15, xlim=c(0,6), ylim = c(0, 1.5),
       main = paste("Sample Size =", size))
  
  cat("Sample Size = ", size, " Mean = ", mean(xbar),
      " SD = ", sd(xbar), "\n")
}

freq.4
sample.1$genre

psample1 <- plot_ly(x = sample.4$genre, type="histogram", name = 'Top 5 Categories of Sample')
psample2 <- plot_ly(x = sample.1$genre, type = "histogram", name = "SRSWOR")
psample3 <- plot_ly(x = sample.2$genre, type = "histogram", name = "Systemic Sampling")
psample4 <- plot_ly(x = sample.3$genre, type = "histogram", name = "Stratified Sampling")

psample <- subplot(psample1, psample2, psample3, psample4, nrows = 2) %>%
  layout(title = list(text = "Top 5 Genres of Spotify Top Hits"),
          xaxis = list(title = "Song Genre"),
          yaxis = list(title = "Songs")
          )

psample

SpotifyTopHitsPlot<- SpotifyTopHits |>
  group_by(year) |>
  summarise(acousticness = mean(acousticness),
            danceability = mean(danceability),
            instrumentalness = mean(instrumentalness),
            energy = mean(energy),
            speechiness = mean(speechiness),
            liveness = mean(liveness),
            valence = mean(valence))

SpotifyTopHitsPlot |>
  plot_ly(x = ~year, y = ~ danceability, type="scatter", mode = "lines", name = 'danceability') |>
  add_trace(x = ~year, y = ~energy, name = 'energy') |>
  add_trace(x = ~year, y = ~liveness, name = 'liveness') |>
  add_trace(x = ~year, y = ~valence, name = 'valence') |>
  add_trace(x = ~year, y = ~instrumentalness, name = 'instrumentalness') |>
  add_trace(x = ~year, y = ~acousticness, name = 'acousticness') |>
  add_trace(x = ~year, y = ~speechiness, name = 'speechiness') |>
  layout(
    title = "Song Attributes by Year",
    xaxis = list(title = "Metrics"),
    yaxis = list(title = "Score")
  )


table(round(SpotifyTopHits$tempo,0))
max(table(round(SpotifyTopHits$tempo,0)))

