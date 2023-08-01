# R code to reproduce charts from "Computational principles underlying the 
# evolution of cultural learning mechanisms"talk by Xavier Roberts-Gaal at 
# CogSci 2023

##### Housekeeping #####

if (!require("pacman")) { install.packages("pacman"); require("pacman") }
pacman::p_load(tidyverse, scales, rstudioapi, svglite)

setwd(dirname(getActiveDocumentContext()$path))
source(paste0(file.path(getwd(), ".."), "/theme_mprl_ggplot.R")) # Lab ggplot theme

theme_set(theme_mprl())

##### Load data #####

df_model1 <- read_csv("data/model1_simulations_aggregated.csv") %>%
  mutate(prop = count/120,
         across(where(is.numeric), ~ round(., 4)),
         model = "1")

df_model1_payoffs <- read_csv("data/model1_simulations_aggregated_payoffs.csv") %>%
  mutate(across(where(is.numeric), ~ round(., 4)))

df_model2 <- read_csv("data/model2_simulations_aggregated.csv") %>%
  mutate(Lambda = lambda,
         prop = count/120,
         across(where(is.numeric), ~ round(., 4)),
         model = "2") %>%
  filter(kappa == 0.4, 
         lambda %in% c(0.1, 0.2, 0.3))

df_model2_payoffs <- read_csv("data/model2_simulations_aggregated_payoffs.csv") %>%
  mutate(across(where(is.numeric), ~ round(., 4)))

##### 1 #####

(fig_slides_1 <- ggplot(df_model1, aes(x = delta, y = prop, fill = strategy)) +
   stat_smooth(geom = "area",
               position = "fill",
               method = "loess",
               span = 1/10) +
   scale_x_continuous(n.breaks = 10, name = "Shock probability") +
   ylab("Concentration of type") +
   scale_fill_manual(values = c("IL" = "darkgrey", "MF" = "orange")))

##### 2 #####

(fig_slides_2 <- ggplot(df_model1_payoffs, aes(x = delta, y = avg_payoff, color = strategy)) +
   geom_smooth() +
   scale_x_continuous(n.breaks = 10, name = "Shock probability") +
   ylab("Average payoff by type") +
   scale_color_manual(values = c("IL" = "darkgrey", "MF" = "orange")))

##### 3 #####

(fig_slides_3 <- ggplot(data = df_model2, 
                aes(x = delta, y = prop, color = strategy)) +
    scale_color_manual(values = c("IL" = "darkgrey", "MB" = "blue", "MF" = "orange")) +
    guides(color = guide_legend(title = "Strategy")) +
    scale_x_continuous(n.breaks = 5, labels = label_number(accuracy = 0.01), 
                       name = "Shock probability") +
    scale_y_continuous(n.breaks = 5, labels = label_number(accuracy = 0.01), 
                       limits = c(0, 1), name = "Concentration of type") +
    geom_jitter(width = 0.01, height = 0.01, alpha = 0.4, size = 0.3) +
    geom_smooth(aes(x = delta, y = prop), formula = y ~ x, method = "lm", se=F) +
    facet_wrap( ~ Lambda, nrow = 3, labeller = lambda_labeller))

plot_fig3 <- function(df, value) {
  out <- ggplot(data = df %>% filter(lambda == value),
         aes(x = delta, y = prop, fill = strategy)) +
    scale_fill_manual(values = c("IL" = "darkgrey", "MB" = "blue", "MF" = "orange")) +
    guides(color = guide_legend(title = "Strategy")) +
    scale_x_continuous(n.breaks = 11, labels = label_number(accuracy = 0.01),
                       name = "Shock probability") +
    scale_y_continuous(n.breaks = 5, labels = label_number(accuracy = 0.01),
                       name = "Type concentration") +
    stat_smooth(geom = "area",
                position = "fill",
                method = "loess",
                span = 1/10)

  return(out)
}

(fig_slides_3_area_a <- plot_fig3(df_model2, 0.1))

(fig_slides_3_area_b <- plot_fig3(df_model2, 0.2))

(fig_slides_3_area_c <- plot_fig3(df_model2, 0.3))

##### 4 #####

# Compare concentration of social learners from model 1 and model 2
df_4a <- df_model1 %>% 
  pivot_wider(names_from = strategy,
              values_from = prop) %>%
  mutate(SL = MF) %>%
  dplyr::select(model, SL, delta, kappa) %>%
  drop_na()

df_4b <- df_model2 %>% 
  dplyr::select(-count) %>%
  pivot_wider(names_from = strategy,
              values_from = prop) %>%
  mutate(SL = MF + MB) %>%
  dplyr::select(model, SL, delta, kappa)

df_slides_4 <- rbind(df_4a, df_4b)
df_slides_4$model <- factor(df_slides_4$model, levels = c("1", "2"))

# Creates chart
(fig_slides_4 <- ggplot(data = df_slides_4, aes(x = delta, y = SL, color = model)) +
  geom_point(alpha = 0.1, size = 0.5) +
  geom_smooth(linewidth = 1.5) +
  scale_color_manual(labels = c("1: SL", "2: MF+MB"), values = c("2" = "#0D0887FF", "1" = "#ED7953FF")) +
  xlab("Shock probability") +
  ylab("Social learner concentration")) +
  theme(legend.position = "none")


##### 5 #####


df_single_run <- read_csv("data/data_size=120_gens=5000_Delta=0.2_Lambda=0.2_Kappa=0.4_seed=46.csv")

df_single_run_counts <- df_single_run %>% group_by(gen, strategy) %>% summarize(n = n())

ggplot(df_single_run_counts, aes(x = gen, y = n, color = strategy)) +
  geom_point(alpha = 0.2, size = 0.5) +
  geom_smooth() + 
  geom_vline(xintercept = 2500)

ggplot(df_single_run_counts, aes(x = gen, y = n, color = strategy, fill = strategy)) +
  stat_smooth(geom = "area",
              position = "fill",
              method = "loess",
              span = 1/10) +
  geom_vline(xintercept = 2500) +
  scale_fill_manual(values = c("IL" = "darkgrey", "MB" = "blue", "MF" = "orange"))

