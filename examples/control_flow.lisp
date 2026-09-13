(begin
  (set passo 1)

  (while (<= passo 4)
    (begin
      (if (>= passo 3)
        (print passo)
        (print 0)
      )

      (set passo (+ passo 1))
    )
  )
)
